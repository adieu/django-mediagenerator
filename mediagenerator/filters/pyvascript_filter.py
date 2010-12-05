from mediagenerator.generators.bundles.base import Filter, RawFileFilter
from pyvascript.grammar import compile
import os
import pyvascript

class PyvaScript(Filter):
    def __init__(self, **kwargs):
        super(PyvaScript, self).__init__(**kwargs)
        assert self.filetype == 'js', (
            'PyvaScript only supports compilation to js. '
            'The parent filter expects "%s".' % self.filetype)
        self.input_filetype = 'pyvascript'

    def should_use_default_filter(self, ext):
        if ext == 'pyva':
            return False
        return super(PyvaScript, self).should_use_default_filter(ext)

    def get_output(self, variation):
        for input in self.get_input(variation):
            yield compile(input)

    def get_dev_output(self, name, variation):
        content = super(PyvaScript, self).get_dev_output(name, variation)
        return compile(content)

    def get_item(self, name):
        if name == '.stdlib.pyva':
            path = os.path.join(os.path.dirname(pyvascript.__file__),
                                'stdlib.pyva')
            return RawFileFilter(name='.stdlib.pyva', path=path)
        return super(PyvaScript, self).get_item(name)
