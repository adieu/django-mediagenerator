from django.conf import settings
from django.utils.encoding import smart_str
from hashlib import sha1
from mediagenerator.generators.bundles.base import Filter
from mediagenerator.utils import get_media_dirs, find_file, read_text_file
from subprocess import Popen, PIPE
import os
import posixpath
import re
import sys

# Emits extra debug info that can be used by the FireSass Firebug plugin
SASS_DEBUG_INFO = getattr(settings, 'SASS_DEBUG_INFO', False)
SASS_FRAMEWORKS = getattr(settings, 'SASS_FRAMEWORKS',
                          ('compass', 'blueprint'))
if isinstance(SASS_FRAMEWORKS, basestring):
    SASS_FRAMEWORKS = (SASS_FRAMEWORKS,)

_RE_FLAGS = re.MULTILINE | re.UNICODE
multi_line_comment_re = re.compile(r'/\*.*?\*/', _RE_FLAGS | re.DOTALL)
one_line_comment_re = re.compile(r'//.*', _RE_FLAGS)
import_re = re.compile(r'^@import\s+["\']?(.+?)["\']?\s*;?\s*$', _RE_FLAGS)

class Sass(Filter):
    takes_input = False

    def __init__(self, **kwargs):
        self.config(kwargs, path=(), main_module=None)
        if isinstance(self.path, basestring):
            self.path = (self.path,)
        super(Sass, self).__init__(**kwargs)
        assert self.filetype == 'css', (
            'Sass only supports compilation to css. '
            'The parent filter expects "%s".' % self.filetype)
        assert self.main_module, \
            'You must provide a main module'

        self.path += tuple(get_media_dirs())
        self.path_args = []
        for path in self.path:
            self.path_args.extend(('-I', path.replace('\\', '/')))

        self._compiled = None
        self._compiled_hash = None
        self._dependencies = {}

    @classmethod
    def from_default(cls, name):
        return {'main_module': name}

    def get_output(self, variation):
        self._regenerate(debug=False)
        yield self._compiled

    def get_dev_output(self, name, variation):
        assert name == self.main_module
        self._regenerate(debug=True)
        return self._compiled

    def get_dev_output_names(self, variation):
        self._regenerate(debug=True)
        yield self.main_module, self._compiled_hash

    def _compile(self, debug=False):
        extensions = os.path.join(os.path.dirname(__file__), 'sass_compass.rb')
        extensions = extensions.replace('\\', '/')
        run = ['sass', '-C', '-t', 'expanded',
               '--require', extensions]
        for framework in SASS_FRAMEWORKS:
            # Some frameworks are loaded by default
            if framework in ('blueprint', 'compass'):
                continue
            run.extend(('--require', framework))
        if debug:
            run.append('--line-numbers')
            if SASS_DEBUG_INFO:
                run.append('--debug-info')
        run.extend(self.path_args)
        shell = sys.platform == 'win32'
        try:
            cmd = Popen(run, shell=shell, universal_newlines=True,
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
            module = self.main_module.rsplit('.', 1)[0]
            output, error = cmd.communicate('@import "%s"' % module)
            assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
            output = output.decode('utf-8')
            if output.startswith('@charset '):
                output = output.split(';', 1)[1]
            return output
        except Exception, e:
            raise ValueError("Failed to execute Sass. Please make sure that "
                "you have installed Sass (http://sass-lang.com) and "
                "Compass (http://compass-style.org).\n"
                "Error was: %s" % e)

    def _regenerate(self, debug=False):
        if self._dependencies:
            for name, mtime in self._dependencies.items():
                path = self._find_file(name)
                if not path or os.path.getmtime(path) != mtime:
                    # Just recompile everything
                    self._dependencies = {}
                    break
            else:
                # No changes
                return

        modules = [self.main_module]
        while True:
            if not modules:
                break

            module_name = modules.pop()
            path = self._find_file(module_name)
            assert path, 'Could not find the Sass module %s' % module_name
            mtime = os.path.getmtime(path)
            self._dependencies[module_name] = mtime

            source = read_text_file(path)
            dependencies = self._get_dependencies(source)

            for name in dependencies:
                # Try relative import, first
                transformed = posixpath.join(posixpath.dirname(module_name), name)
                path = self._find_file(transformed)
                if path:
                    name = transformed
                else:
                    path = self._find_file(name)
                assert path, ('The Sass module %s could not find the '
                              'dependency %s' % (module_name, name))
                if name not in self._dependencies:
                    modules.append(name)

        self._compiled = self._compile(debug=debug)
        self._compiled_hash = sha1(smart_str(self._compiled)).hexdigest()

    def _get_dependencies(self, source):
        clean_source = multi_line_comment_re.sub('\n', source)
        clean_source = one_line_comment_re.sub('', clean_source)
        return [name for name in import_re.findall(clean_source)
                if not name.endswith('.css')]

    def _find_file(self, name):
        parts = name.rsplit('/', 1)
        parts[-1] = '_' + parts[-1]
        partial = '/'.join(parts)
        if not name.endswith(('.sass', '.scss')):
            names = (name + '.sass', name + '.scss', partial + '.sass',
                     partial + '.scss')
        else:
            names = (name, partial)
        for name in names:
            path = find_file(name, media_dirs=self.path)
            if path:
                return path
