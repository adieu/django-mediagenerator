from django.conf import settings
from django.utils.encoding import smart_str

from mediagenerator.generators.bundles.base import Filter
from mediagenerator.utils import get_media_dirs, find_file

import os, sys
from hashlib import sha1
from subprocess import Popen, PIPE

class HandlebarsFilter(Filter):
    def __init__(self, **kwargs):
        self.config(kwargs, name=kwargs["name"], path=(), template_name=kwargs.get("template_name"))
        if isinstance(self.path, basestring):
            self.path = (self.path,)

        # we need to be able to mutate self.path
        self.path = list(self.path)

        super(HandlebarsFilter, self).__init__(**kwargs)

        media_dirs = [directory for directory in get_media_dirs()
                      if os.path.exists(directory)]
        self.path += tuple(media_dirs)

        # search from template directories first
        from django.template.loaders.app_directories import app_template_dirs
        self.path = list(app_template_dirs) + self.path

        self._compiled = None
        self._compiled_hash = None
        self._dependencies = {}


    @classmethod
    def from_default(cls, name):
        return {'name': name}

    def get_output(self, variation):
        self._regenerate(debug=False)
        yield self._compiled

    def get_dev_output(self, name, variation):
        self._regenerate(debug=True)
        return self._compiled

    def get_dev_output_names(self, variation):
        self._regenerate(debug=True)
        yield self.name + '.js', self._compiled_hash


    def _regenerate(self, debug=False):
        file_path = self._find_file(self.name)
        self._compiled = self._compile(file_path, debug=debug)
        self._compiled_hash = sha1(smart_str(self._compiled)).hexdigest()

    def _compile(self, path, debug=False):
        # check if already compiled
        if hasattr(self, "mtime") and self.mtime == os.path.getmtime(path):
            return self._compiled

        # compile with handlebars
        try:
            shell = sys.platform == 'win32'

            relative_path = self._get_relative_path(path)

            cmd = Popen(['handlebars', relative_path],
                        stdin=PIPE, stdout=PIPE, stderr=PIPE,
                        shell=shell, universal_newlines=True,
                        cwd=settings.PROJECT_ROOT)
            output, error = cmd.communicate()

            self.mtime = os.path.getmtime(path)

            assert cmd.wait() == 0, ('handlebars returned errors:\n%s\n%s' % (error, output))
            return output.decode('utf-8')
        except Exception, e:
            raise ValueError("Failed to run handlebars.js compiler for this "
                "file. Please confirm that the \"handlebars\" application is "
                "on your path and that you can run it from your own command "
                "line.\n"
                "Error was: %s" % e)


    def _find_file(self, name):
        return find_file(name, media_dirs=self.path)


    def _get_relative_path(self, abs_path):
        """Given an absolute path, return a path relative to the
        project root.
        'subdir/foo'

        """
        relative_path = os.path.relpath(abs_path, settings.PROJECT_ROOT)
        return relative_path
