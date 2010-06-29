from mediagenerator.base import Filter
from pyjs.translator import import_compiler, Translator

from cStringIO import StringIO

class Pyjs(Filter):
    def __init__(self, **kwargs):
        super(Pyjs, self).__init__(**kwargs)
        assert self.filetype == 'js', (
            'Pyjs only supports compilation to js. '
            'The parent filter expects "%s".' % self.filetype)
        self.input_filetype = 'pyjs'

    def get_output(self, variation):
        for input in self.get_input(variation):
            yield self.compile(input)

    def get_dev_output(self, name, variation):
        content = super(PyvaScript, self).get_dev_output(name, variation)
        return self.compile(content)

    def compile(self, source):
        compiler = import_compiler(False)
        tree = compiler.parse(source)
        output = StringIO()
        Translator(compiler, 'test', 'test2', source, tree, output)
        return output.getvalue()
