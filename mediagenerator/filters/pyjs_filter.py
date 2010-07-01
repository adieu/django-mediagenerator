from django.conf import settings
from hashlib import sha1
from mediagenerator.base import Filter
from pyjs.translator import import_compiler, Translator, LIBRARY_PATH
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

PYJS_INIT_LIB_PATH = os.path.join(LIBRARY_PATH, 'builtin', 'public', '_pyjs.js')
BUILTIN_PATH = os.path.join(LIBRARY_PATH, 'builtin')
STDLIB_PATH = os.path.join(LIBRARY_PATH, 'lib')
EXTRA_LIBS_PATH = os.path.join(os.path.dirname(__file__), 'pyjslibs')

INIT_CODE = """
var $wnd = window;
var $doc = window.document;
var $pyjs = new Object();
$pyjs.global_namespace = this;
$pyjs.__modules__ = {};
$pyjs.modules_hash = {};
$pyjs.loaded_modules = {};
$pyjs.options = new Object();
$pyjs.options.arg_ignore = true;
$pyjs.options.arg_count = true;
$pyjs.options.arg_is_instance = true;
$pyjs.options.arg_instance_type = true;
$pyjs.options.arg_kwarg_dup = true;
$pyjs.options.arg_kwarg_unexpected_keyword = true;
$pyjs.options.arg_kwarg_multiple_values = true;
$pyjs.options.set_all(true);
$pyjs.options.dynamic_loading = false;
$pyjs.trackstack = [];
$pyjs.track = {module:'__main__', lineno: 1};
$pyjs.trackstack.push($pyjs.track);
$pyjs.__last_exception_stack__ = null;
$pyjs.__last_exception__ = null;
""".lstrip()

class Pyjs(Filter):
    takes_input = False

    def __init__(self, **kwargs):
        self.config(kwargs, exclude_main_libs=False, main_module=None,
                    debug=None, path=(), only_dependencies=None)
        if isinstance(self.path, basestring):
            self.path = (self.path,)
        if self.only_dependencies is None:
            self.only_dependencies = bool(self.main_module)
        if self.only_dependencies:
            self.path += (STDLIB_PATH, BUILTIN_PATH, EXTRA_LIBS_PATH)
        super(Pyjs, self).__init__(**kwargs)
        assert self.filetype == 'js', (
            'Pyjs only supports compilation to js. '
            'The parent filter expects "%s".' % self.filetype)

        if self.only_dependencies:
            assert self.main_module, \
                'You must provide a main module in only_dependencies mode'

        self._compiled = {}
        self._collected = {}

    def get_output(self, variation):
        self._collect_all_modules()

        if not self.exclude_main_libs:
            yield self._compile_init()

        if self.only_dependencies:
            self._regenerate(dev_mode=False)
            for name in sorted(self._compiled.keys()):
                yield self._compiled[name][1]
        else:
            for name in sorted(self._collected.keys()):
                fp = open(self._collected[name], 'r')
                output = self._compile(name, fp.read(), dev_mode=False)[0]
                fp.close()
                yield output

        yield self._compile_main()

    def get_dev_output(self, name, variation):
        self._collect_all_modules()
        
        name = name.split('/', 1)[-1]

        if name == '.init.js':
            return self._compile_init()
        elif name == '.main.js':
            return self._compile_main()

        if self.only_dependencies:
            self._regenerate(dev_mode=True)
            return self._compiled[name][1]
        else:
            fp = open(self._collected[name], 'r')
            output = self._compile(name, fp.read(), dev_mode=True)[0]
            fp.close()
            return output

    def get_dev_output_names(self, variation):
        self._collect_all_modules()

        if not self.exclude_main_libs:
            yield '.init.js'

        if self.only_dependencies:
            self._regenerate(dev_mode=True)
            for name in sorted(self._compiled.keys()):
                yield '%s/%s' % (self._compiled[name][2], name)
        else:
            for name in sorted(self._collected.keys()):
                yield name

        if self.main_module is not None or not self.exclude_main_libs:
            yield '.main.js'

    def _regenerate(self, dev_mode=False):
        # This function is only called in only_dependencies mode
        if self._compiled:
            for module_name, (mtime, content, hash) in self._compiled.items():
                if module_name not in self._collected or \
                        os.path.getmtime(self._collected[module_name]) != mtime:
                    # Just recompile everything
                    # TODO: track dependencies and changes and recompile only
                    # what's necessary
                    self._compiled = {}
                    break
            else:
                # No changes
                return

        modules = [self.main_module, 'pyjslib']
        while True:
            if not modules:
                break

            module_name = modules.pop()
            path = self._collected[module_name]
            mtime = os.path.getmtime(path)

            fp = open(path, 'r')
            source = fp.read()
            fp.close()

            content, py_deps, js_deps = self._compile(module_name, source, dev_mode=dev_mode)
            hash = sha1(content).hexdigest()
            self._compiled[module_name] = (mtime, content, hash)

            for name in py_deps:
                if name not in self._collected:
                    if '.' in name and name.rsplit('.', 1)[0] in self._collected:
                        name = name.rsplit('.', 1)[0]
                    else:
                        raise ImportError('The pyjs module %s could not find '
                            'the dependency %s' % (module_name, name))
                if name not in self._compiled:
                    modules.append(name)

    def _compile(self, name, source, dev_mode=False):
        if self.debug is None:
            debug = dev_mode
        else:
            debug = self.debug
        compiler = import_compiler(False)
        tree = compiler.parse(source)
        output = StringIO()
        translator = Translator(compiler, name, name, source, tree, output,
            debug=debug, source_tracking=debug, line_tracking=debug,
            store_source=debug)
        return output.getvalue(), translator.imported_modules, translator.imported_js

    def _compile_init(self):
        fp = open(PYJS_INIT_LIB_PATH, 'r')
        content = fp.read()
        fp.close()
        return INIT_CODE + content

    def _compile_main(self):
        content = ''
        if not self.exclude_main_libs:
            content += '\n\n$pyjs.loaded_modules["pyjslib"]("pyjslib");'
            content += '\n$pyjs.__modules__.pyjslib = $pyjs.loaded_modules["pyjslib"];'
        if self.main_module is not None:
            content += '\n\npyjslib.___import___("%s", null, "__main__");' % self.main_module
        return content

    def _collect_all_modules(self):
        """Collect modules, so we can handle imports later"""
        for pkgroot in self.path:
            pkgroot = os.path.abspath(pkgroot)
            for root, dirs, files in os.walk(pkgroot):
                if '__init__.py' in files:
                    files.remove('__init__.py')
                    # The root __init__.py is ignored
                    if root != pkgroot:
                        files.insert(0, '__init__.py')
                elif root != pkgroot:
                    # Only add valid Python packages
                    dirs[:] = []
                    continue

                for filename in files:
                    if not filename.endswith('.py'):
                        continue

                    path = os.path.join(root, filename)
                    module_path = path[len(pkgroot)+len(os.sep):]
                    if os.path.basename(module_path) == '__init__.py':
                        module_name = os.path.dirname(module_path)
                    else:
                        module_name = module_path[:-3]
                    assert '.' not in module_name, \
                        'Invalid module file name: %s' % module_path
                    module_name = module_name.replace(os.sep, '.')

                    self._collected.setdefault(module_name, path)
