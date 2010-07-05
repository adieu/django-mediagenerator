from django.conf import settings
from mediagenerator.generators.groups.base import Filter
from subprocess import Popen, PIPE

class YUICompressor(Filter):
    def __init__(self, **kwargs):
        self.config(kwargs, separate_files=False)
        if not self.separate_files:
            kwargs['input'] = [{'filter': 'mediagenerator.filters.concat.Concat',
                                'input': kwargs.pop('input')}]
        super(YUICompressor, self).__init__(**kwargs)
        assert self.filetype in ('css', 'js'), (
            'YUICompressor only supports compilation to css and js. '
            'The parent filter expects "%s".' % self.filetype)

    def get_output(self, variation):
        for input in self.get_input(variation):
            try:
                compressor = settings.YUICOMPRESSOR_PATH
                cmd = Popen(['java', '-jar', compressor,
                             '--charset', 'utf-8', '--type', self.filetype],
                            stdin=PIPE, stdout=PIPE, stderr=PIPE,
                            universal_newlines=True)
                output, error = cmd.communicate(input)
                assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
                yield output
            except Exception, e:
                raise ValueError("Failed to execute Java VM or yuicompressor. "
                    "Please make sure that you have installed Java "
                    "and that it's in your PATH and that you've configured "
                    "YUICOMPRESSOR_PATH in your settings correctly.\n"
                    "Error was: %s" % e)
