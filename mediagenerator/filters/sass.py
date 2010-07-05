from mediagenerator.generators.groups.base import Filter
from mediagenerator.utils import get_media_dirs
from subprocess import Popen, PIPE

# TODO: also keep track of included files' changes

class Sass(Filter):
    def __init__(self, **kwargs):
        self.config(kwargs, path=())
        if isinstance(self.path, basestring):
            self.path = (self.path,)
        super(Sass, self).__init__(**kwargs)
        assert self.filetype == 'css', (
            'Sass only supports compilation to css. '
            'The parent filter expects "%s".' % self.filetype)

        self.input_filetype = 'sass'

        self.path += tuple(get_media_dirs())
        self.path_args = []
        for path in self.path:
            self.path_args.extend(('-I', path))

    def should_use_default_filter(self, ext):
        if ext == 'sass':
            return False
        return super(PyvaScript, self).should_use_default_filter(ext)

    def get_output(self, variation):
        for input in self.get_input(variation):
            yield self._compile(input)

    def get_dev_output(self, name, variation):
        input = super(Sass, self).get_dev_output(name, variation)
        return self._compile(input)

    def _compile(self, input):
        cmd = Popen(['sass', '-C', '-t', 'expanded', '-E', 'utf-8']
                    + self.path_args, shell=True, universal_newlines=True,
                    stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, error = cmd.communicate(input)
        assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
        return output
