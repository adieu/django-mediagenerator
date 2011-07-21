from django.conf import settings
from hashlib import sha1
from mediagenerator.base import Generator
from mediagenerator.utils import get_media_dirs, find_file, prepare_patterns
from mimetypes import guess_type
import os
import sys

COPY_MEDIA_FILETYPES = getattr(settings, 'COPY_MEDIA_FILETYPES',
    ('gif', 'jpg', 'jpeg', 'png', 'svg', 'svgz', 'ico', 'swf', 'ttf', 'otf',
     'eot', 'woff'))

IGNORE_PATTERN = prepare_patterns(getattr(settings,
   'IGNORE_MEDIA_COPY_PATTERNS', ()), 'IGNORE_MEDIA_COPY_PATTERNS')


class CopyFiles(Generator):
    def get_dev_output(self, name):
        path = find_file(name)
        fp = open(path, 'rb')
        content = fp.read()
        fp.close()
        mimetype = guess_type(path)[0]
        return content, mimetype

    def get_dev_output_names(self):
        media_files = {}
        for root in get_media_dirs():
            self.collect_copyable_files(media_files, root)

        for name, source in media_files.items():
            fp = open(source, 'rb')
            hash = sha1(fp.read()).hexdigest()
            fp.close()
            yield name, name, hash

    def collect_copyable_files(self, media_files, root):
        #python 2.5 does not have the followlinks keyword argument
        has_followlinks = sys.version_info >= (2, 6)
        if has_followlinks:
            allfiles = os.walk(root, followlinks=True)
        else:
            allfiles = os.walk(root)

        for root_path, dirs, files in allfiles:
            for file in files:
                ext = os.path.splitext(file)[1].lstrip('.')
                path = os.path.join(root_path, file)
                if not has_followlinks:
                    path = os.path.abspath(path)
                media_path = path[len(root) + 1:].replace(os.sep, '/')
                if ext in COPY_MEDIA_FILETYPES and \
                        not IGNORE_PATTERN.match(media_path):
                    media_files[media_path] = path
