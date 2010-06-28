from django.conf import settings
from mediagenerator.base import Filter
from subprocess import Popen, PIPE
import os

class YUICompressor(Filter):
    def __init__(self, **kwargs):
        self.config(kwargs, separate_files=False)
        if self.separate_files:
            kwargs['input'] = [{'filter': 'mediagenerator.filters.concat.ConcatFilter',
                                'input': kwargs.pop('input')}]
        super(YUICompressor, self).__init__(**kwargs)

    def get_output(self, variation):
        if not self.filetype in ('css', 'js'):
            raise ValueError('YUICompressor only supports CSS and JS files')

        for input in self.get_input(variation):
            try:
                compressor = settings.YUICOMPRESSOR_PATH
                cmd = Popen(['java', '-jar', compressor], stdin=PIPE, stdout=PIPE)
                output = cmd.communicate(input)[0]
                yield output.replace(os.linesep, '\n')
            except Exception, e:
                raise ValueError("Failed to execute Java VM or yuicompressor. "
                    "Please make sure that you have installed Java "
                    "and that it's in your PATH and that you've configured "
                    "YUICOMPRESSOR_PATH in your settings correctly.\n"
                    "Error was: %r" % e)
