from django.utils.encoding import smart_str
from hashlib import sha1
from mediagenerator.generators.bundles.base import Filter
from mediagenerator.utils import get_media_dirs, read_text_file
from pyjs.translator import import_compiler, Translator, LIBRARY_PATH
from textwrap import dedent
import os
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

# Register PYVA() function
try:
    from pyvascript.grammar import compile
    from pyjs.translator import native_js_func

    @native_js_func
    def PYVA(content, unescape, is_statement, **kwargs):
        result = compile(dedent(unescape(content)))
        if not is_statement:
            return result.strip().rstrip('\r\n\t ;')
        return result
except ImportError:
    # No PyvaScript installed
    pass

_HANDLE_EXCEPTIONS = """
  } finally { $pyjs.in_try_except -= 1; }
} catch(err) {
  pyjslib['_handle_exception'](err);
}
"""

PYJS_INIT_LIB_PATH = os.path.join(LIBRARY_PATH, 'builtin', 'public', '_pyjs.js')
BUILTIN_PATH = os.path.join(LIBRARY_PATH, 'builtin')
STDLIB_PATH = os.path.join(LIBRARY_PATH, 'lib')
EXTRA_LIBS_PATH = os.path.join(os.path.dirname(__file__), 'pyjslibs')

_LOAD_PYJSLIB = """

$p = $pyjs.loaded_modules["pyjslib"];
$p('pyjslib');
$pyjs.__modules__.pyjslib = $p['pyjslib']
"""

INIT_CODE = """
var $wnd = window;
var $doc = window.document;
var $pyjs = new Object();
var $p = null;
$pyjs.platform = 'safari';
$pyjs.global_namespace = this;
$pyjs.__modules__ = {};
$pyjs.modules_hash = {};
$pyjs.loaded_modules = {};
$pyjs.options = new Object();
$pyjs.options.arg_ignore = true;
$pyjs.options.arg_count = true;
$pyjs.options.arg_is_instance = true;
$pyjs.options.arg_instance_type = false;
$pyjs.options.arg_kwarg_dup = true;
$pyjs.options.arg_kwarg_unexpected_keyword = true;
$pyjs.options.arg_kwarg_multiple_values = true;
$pyjs.options.dynamic_loading = false;
$pyjs.trackstack = [];
$pyjs.track = {module:'__main__', lineno: 1};
$pyjs.trackstack.push($pyjs.track);
$pyjs.__active_exception_stack__ = null;
$pyjs.__last_exception_stack__ = null;
$pyjs.__last_exception__ = null;
$pyjs.in_try_except = 0;
""".lstrip()

class Pyjs(Filter):
    takes_input = False

    def __init__(self, **kwargs):
        self.config(kwargs, exclude_main_libs=False, main_module=None,
                    debug=None, path=(), only_dependencies=None)
        if isinstance(self.path, basestring):
            self.path = (self.path,)
        self.path += tuple(get_media_dirs())
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

    @classmethod
    def from_default(cls, name):
        return {'main_module': name.rsplit('.', 1)[0].replace('/', '.')}

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
                source = read_text_file(self._collected[name])
                yield self._compile(name, source, dev_mode=False)[0]

        yield self._compile_main(dev_mode=False)

    def get_dev_output(self, name, variation):
        self._collect_all_modules()

        name = name.split('/', 1)[-1]

        if name == '._pyjs.js':
            return self._compile_init()
        elif name == '.main.js':
            return self._compile_main(dev_mode=True)

        if self.only_dependencies:
            self._regenerate(dev_mode=True)
            return self._compiled[name][1]
        else:
            source = read_text_file(self._collected[name])
            return self._compile(name, source, dev_mode=True)[0]

    def get_dev_output_names(self, variation):
        self._collect_all_modules()

        if not self.exclude_main_libs:
            content = self._compile_init()
            hash = sha1(smart_str(content)).hexdigest()
            yield '._pyjs.js', hash

        if self.only_dependencies:
            self._regenerate(dev_mode=True)
            for name in sorted(self._compiled.keys()):
                yield name, self._compiled[name][2]
        else:
            for name in sorted(self._collected.keys()):
                yield name, None

        if self.main_module is not None or not self.exclude_main_libs:
            content = self._compile_main(dev_mode=True)
            hash = sha1(smart_str(content)).hexdigest()
            yield '.main.js', hash

    def _regenerate(self, dev_mode=False):
        # This function is only called in only_dependencies mode
        if self._compiled:
            for module_name, (mtime, content, hash) in self._compiled.items():
                if module_name not in self._collected or \
                        not os.path.exists(self._collected[module_name]) or \
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

            source = read_text_file(path)

            try:
                content, py_deps, js_deps = self._compile(module_name, source, dev_mode=dev_mode)
            except:
                self._compiled = {}
                raise
            hash = sha1(smart_str(content)).hexdigest()
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
            # Debug options
            debug=debug, source_tracking=debug, line_tracking=debug,
            store_source=debug,
            # Speed and size optimizations
            function_argument_checking=debug, attribute_checking=False,
            inline_code=False, number_classes=False,
            # Sufficient Python conformance
            operator_funcs=True, bound_methods=True, descriptors=True,
        )
        return output.getvalue(), translator.imported_modules, translator.imported_js

    def _compile_init(self):
        return INIT_CODE + read_text_file(PYJS_INIT_LIB_PATH)

    def _compile_main(self, dev_mode=False):
        if self.debug is None:
            debug = dev_mode
        else:
            debug = self.debug
        content = ''
        if not self.exclude_main_libs:
            content += _LOAD_PYJSLIB
        if self.main_module is not None:
            content += '\n\n'
            if debug:
                content += 'try {\n'
                content += '  try {\n'
                content += '    $pyjs.in_try_except += 1;\n    '
            content += 'pyjslib.___import___("%s", null, "__main__");' % self.main_module
            if debug:
                content += _HANDLE_EXCEPTIONS
        return content

    def _collect_all_modules(self):
        """Collect modules, so we can handle imports later"""
        for pkgroot in self.path:
            pkgroot = os.path.abspath(pkgroot)

            #python 2.5 does not have the followlinks keyword argument
            has_followlinks = sys.version_info >= (2, 6)
            if has_followlinks:
                allfiles = os.walk(pkgroot, followlinks=True)
            else:
                allfiles = os.walk(pkgroot)

            for root, dirs, files in allfiles:
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
                    if not has_followlinks:
                        path = os.path.abspath(path)
                    module_path = path[len(pkgroot) + len(os.sep):]
                    if os.path.basename(module_path) == '__init__.py':
                        module_name = os.path.dirname(module_path)
                    else:
                        module_name = module_path[:-3]
                    assert '.' not in module_name, \
                        'Invalid module file name: %s' % module_path
                    module_name = module_name.replace(os.sep, '.')

                    self._collected.setdefault(module_name, path)
