from django.conf import settings
from mediagenerator.base import Filter
from pyjs.translator import import_compiler, Translator
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class Pyjs(Filter):
    takes_input = False

    def __init__(self, **kwargs):
        self.config(kwargs, with_main_libs=False, main_module=None,
                    debug=settings.DEBUG, path=(),
                    only_dependencies=False)
        if isinstance(self.path, basestring):
            self.path = (self.path,)
        assert self.path and all(map(os.path.isdir, self.path)), (
            'Please provide a valid root folder for Pyjs')
        super(Pyjs, self).__init__(**kwargs)
        assert self.filetype == 'js', (
            'Pyjs only supports compilation to js. '
            'The parent filter expects "%s".' % self.filetype)
        self.input_filetype = 'pyjs'

        self._visited = []
        self._compiled = {}
        self._collected = set()

    def get_output(self, variation):
        if self.with_main_libs:
            yield self._compile_init()
            yield self._compile_pyjslib()

        for name, content in self.get_input(variation):
            yield self.compile(name, content)

        yield self._compile_main()

    def get_dev_output(self, name, variation):
        if name == 'init.js':
            return self._compile_init()
        if name == 'pyjslib.js':
            return self._compile_pyjslib()
        elif name == 'main.js':
            return self._compile_main()

        content = super(Pyjs, self).get_dev_output(name, variation)
        output, js_deps,  self.compile('test', content)

    def get_dev_output_names(self, variation):
        if self.with_main_libs:
            yield 'init.js'
            yield 'pyjslib.js'

        for name in super(Pyjs, self).get_dev_output_names(variation):
            yield name

        if self.main_module is not None or self.with_main_libs:
            yield 'main.js'

    def compile(self, name, source):
        compiler = import_compiler(False)
        tree = compiler.parse(source)
        output = StringIO()
        dependencies = Translator(compiler, name, name, source, tree, output,
            debug=self.debug, source_tracking=self.debug,
            line_tracking=self.debug, store_source=self.debug)
        return output.getvalue(), dependencies[0], dependencies[1]

    def _compile_init(self):
        pass

    def _compile_pyjslib(self):
        pass

    def _compile_main(self):
        content = ''
        if self.with_main_libs:
            content += '\n\npyjslib("pyjslib");'
        if self.main_module is not None:
            content += '\n\n%s("%s");' % (2*(self.main_module,))
        return content

    def _collect_all_modules(self):
        for pkgroot in self.path:
            pkgroot = os.path.abspath(pkgroot)
            for root, dirs, files in os.walk(pkgroot):
                if '__init__.py' in files:
                    files.remove('__init__.py')
                    files.insert(0, '__init__.py')
                else:
                    # Only add valid Python packages
                    dirs[:] = []
                    continue

                for filename in files:
                    if not filename.endswith('.py'):
                        continue

                    path = os.path.join(root, filename)
                    module_path = filename[len(path)+len(os.sep):]

                    if self.options.exclude and \
                       re.match(self.options.exclude, module_path):
                        continue

                    if module_path.endswith('__init__.py'):
                        module_name = os.path.dirname(module_path)
                    else:
                        module_name = module_path[:-3] # cut ".py"
                    module_name = module_name.replace(os.sep, ".")

                    print "%s (%s)" % (module_name, module_path)
                    self.compile(module_path, module_name, self.options.working_dir)
