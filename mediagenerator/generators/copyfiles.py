from django.conf import settings
from hashlib import sha1
from mediagenerator.base import Generator
from mediagenerator.utils import get_media_dirs, find_file
from mimetypes import guess_type
import os
import re

COPY_MEDIA_FILETYPES = getattr(settings, 'COPY_MEDIA_FILETYPES',
    ('gif', 'jpg', 'jpeg', 'png', 'svg', 'ico', 'swf'))

def _prepare_patterns(patterns):
    if isinstance(patterns, basestring):
        patterns = (patterns,)
    if not patterns:
        return None
    # First validate each pattern individually
    for pattern in patterns:
        try:
            re.compile(pattern, re.U)
        except re.error:
            raise ValueError("""Pattern "%s" can't be compiled """
                             "in IGNORE_MEDIA_COPY_PATTERNS")
    # Now return a combined pattern
    return re.compile('|'.join(patterns), re.U)

IGNORE_PATTERN = _prepare_patterns(getattr(settings,
   'IGNORE_MEDIA_COPY_PATTERNS', ()))

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
        for root_path, dirs, files in os.walk(root):
            for file in files:
                ext = os.path.splitext(file)[1].lstrip('.')
                path = os.path.join(root_path, file)
                media_path = path[len(root)+1:].replace(os.sep, '/')
                if ext in COPY_MEDIA_FILETYPES and \
                        not (IGNORE_PATTERN and IGNORE_PATTERN.match(media_path)):
                    media_files[media_path] = path
