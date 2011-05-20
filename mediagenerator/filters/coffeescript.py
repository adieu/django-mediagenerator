from django.utils.encoding import smart_str
from hashlib import sha1
from mediagenerator.generators.bundles.base import Filter
from mediagenerator.utils import find_file, read_text_file
from subprocess import Popen, PIPE
import os
import sys

class CoffeeScript(Filter):
    takes_input = False

    def __init__(self, **kwargs):
        self.config(kwargs, module=None)
        super(CoffeeScript, self).__init__(**kwargs)
        assert self.filetype == 'js', (
            'CoffeeScript only supports compilation to js. '
            'The parent filter expects "%s".' % self.filetype)
        self._compiled = None
        self._compiled_hash = None
        self._mtime = None

    @classmethod
    def from_default(cls, name):
        return {'module': name}

    def get_output(self, variation):
        self._regenerate(debug=False)
        yield self._compiled

    def get_dev_output(self, name, variation):
        assert name == self.module
        self._regenerate(debug=True)
        return self._compiled

    def get_dev_output_names(self, variation):
        self._regenerate(debug=True)
        yield self.module, self._compiled_hash

    def _regenerate(self, debug=False):
        path = find_file(self.module)
        mtime = os.path.getmtime(path)
        if mtime == self._mtime:
            return
        source = read_text_file(path)
        self._compiled = self._compile(source, debug=debug)
        self._compiled_hash = sha1(smart_str(self._compiled)).hexdigest()
        self._mtime = mtime

    def _compile(self, input, debug=False):
        try:
            shell = sys.platform == 'win32'
            cmd = Popen(['coffee', '--compile', '--print', '--stdio', '--bare'],
                        stdin=PIPE, stdout=PIPE, stderr=PIPE,
                        shell=shell, universal_newlines=True)
            output, error = cmd.communicate(smart_str(input))
            assert cmd.wait() == 0, ('CoffeeScript command returned bad '
                                     'result:\n%s' % error)
            return output.decode('utf-8')
        except Exception, e:
            raise ValueError("Failed to run CoffeeScript compiler for this "
                "file. Please confirm that the \"coffee\" application is "
                "on your path and that you can run it from your own command "
                "line.\n"
                "Error was: %s" % e)
