from django.conf import settings
from mediagenerator.base import Filter, FileFilter
from pyvascript.grammar import compile
import os

class PyvaScript(Filter):
    def __init__(self, **kwargs):
        super(PyvaScript, self).__init__(**kwargs)
        self.file_filter = PyvaScriptFileFilter

    def get_output(self, variation):
        if self.filetype != 'js':
            raise ValueError('PyvaScript only supports JS output')

        for input in self.get_input(variation):
            try:
                compressor = settings.YUICOMPRESSOR_PATH
                cmd = Popen(['java', '-jar', compressor], stdin=PIPE, stdout=PIPE)
                output = cmd.communicate(input)[0]
                assert cmd.wait() == 0
                yield output.replace(os.linesep, '\n')
            except Exception, e:
                raise ValueError("Failed to execute Java VM or yuicompressor. "
                    "Please make sure that you have installed Java "
                    "and that it's in your PATH and that you've configured "
                    "YUICOMPRESSOR_PATH in your settings correctly.\n"
                    "Error was: %r" % e)

    def get_item(self, name):
        return PyvaScriptFileFilter(name=name, filetype=self.filetype)

class PyvaScriptFileFilter(FileFilter):
    def convert(self, content):
        return compile(content)
