from hashlib import sha1
from mediagenerator.generators.groups.base import Filter
from mediagenerator.utils import get_media_dirs, find_file
from subprocess import Popen, PIPE
import os
import re

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

        self.input_filetype = 'sass'

        self.path += tuple(get_media_dirs())
        self.path_args = []
        for path in self.path:
            self.path_args.extend(('-I', path))

        self._compiled = None
        self._dependencies = {}

    @classmethod
    def from_default(cls, name):
        return {'main_module': name}

    def should_use_default_filter(self, ext):
        if ext == 'sass':
            return False
        return super(Sass, self).should_use_default_filter(ext)

    def get_output(self, variation):
        self._regenerate()
        yield self._compiled

    def get_dev_output(self, name, variation):
        self._regenerate()
        yield self._compiled

    def get_dev_output_names(self, variation):
        hash = sha1(self._compiled).hexdigest()
        yield self.main_module, hash

    def _compile(self, input):
        cmd = Popen(['sass', '-C', '-t', 'expanded', '-E', 'utf-8']
                    + self.path_args, shell=True, universal_newlines=True,
                    stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, error = cmd.communicate(input)
        assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
        return output

    def _regenerate(self):
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

            fp = open(path, 'r')
            source = fp.read()
            fp.close()

            dependencies = self._get_dependencies(source)

            for name in dependencies:
                path = self._find_file(name)
                assert path, ('The Sass module %s could not find the '
                              'dependency %s' % (module_name, name))
                if name not in self._dependencies:
                    modules.append(name)
        
        path = self._find_file(self.main_module)
        fp = open(path, 'r')
        source = fp.read()
        fp.close()

        self._compiled = self._compile(source)

    def _get_dependencies(self, source):
        clean_source = multi_line_comment_re.sub('\n', source)
        clean_source = one_line_comment_re.sub('', clean_source)
        return [name for name in import_re.findall(clean_source)
                if not name.endswith('.css')]

    def _find_file(self, name):
        if not name.endswith(('.sass', '.scss')):
            names = (name + '.sass', name + '.scss')
        else:
            names = (name,)
        parts = name.rsplit('/', 1)
        parts[-1] = '_' + parts[-1]
        names += ('/'.join(parts),)
        for name in names:
            path = find_file(name, media_dirs=self.path)
            if path:
                return path
