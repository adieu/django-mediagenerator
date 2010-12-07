from mediagenerator.generators.bundles.base import Filter
from subprocess import Popen, PIPE

class CoffeeScript(Filter):    
    def __init__(self, **kwargs):
        super(CoffeeScript, self).__init__(**kwargs)
        assert self.filetype == 'js', (
            'CoffeeScript only supports compilation to js. '
            'The parent filter expects "%s".' % self.filetype)
        self.input_filetype = 'coffee-script'

    def compile(self, input):
        try:
            # coffee
            # -s = Read from stdin for the source
            # -c = Compile
            # -p = print the compiled output to stdout
            cmd = Popen(['coffee', '-c', '-p', '-s', '--no-wrap'],
                        stdin=PIPE, stdout=PIPE, stderr=PIPE,
                        universal_newlines=True)
            output, error = cmd.communicate(input)
            assert cmd.wait() == 0, ('CoffeeScript command returned bad '
                                     'result:\n%s' % error)
            return output
        except Exception, e:
            raise ValueError("Failed to run CoffeeScript compiler for this "
                "file. Please confirm that the \"coffee\" application is "
                "on your path and that you can run it from your own command "
                "line.\n"
                "Error was: %s" % e)

    def should_use_default_filter(self, ext):
        if ext == 'coffee':
            return False
        return super(CoffeeScript, self).should_use_default_filter(ext)

    def get_output(self, variation):
        for input in self.get_input(variation):
            yield self.compile(input)

    def get_dev_output(self, name, variation):
        content = super(CoffeeScript, self).get_dev_output(name, variation)
        return self.compile(content)
