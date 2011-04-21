from . import settings, utils
from .settings import (GENERATED_MEDIA_DIR, GENERATED_MEDIA_NAMES_FILE,
                       MEDIA_GENERATORS)
from .utils import load_backend
from django.utils.http import urlquote
import os
import shutil

def generate_media():
    if os.path.exists(GENERATED_MEDIA_DIR):
        shutil.rmtree(GENERATED_MEDIA_DIR)

    # This will make media_url() generate production URLs
    was_dev_mode = settings.MEDIA_DEV_MODE
    settings.MEDIA_DEV_MODE = False

    utils.NAMES = {}

    for backend_name in MEDIA_GENERATORS:
        backend = load_backend(backend_name)()
        for key, url, content in backend.get_output():
            version = backend.generate_version(key, url, content)
            if version:
                base, ext = os.path.splitext(url)
                url = '%s-%s%s' % (base, version, ext)

            path = os.path.join(GENERATED_MEDIA_DIR, url)
            parent = os.path.dirname(path)
            if not os.path.exists(parent):
                os.makedirs(parent)

            fp = open(path, 'wb')
            if isinstance(content, unicode):
                content = content.encode('utf8')
            fp.write(content)
            fp.close()

            utils.NAMES[key] = urlquote(url)

    settings.MEDIA_DEV_MODE = was_dev_mode

    # Generate a module with media file name mappings
    fp = open(GENERATED_MEDIA_NAMES_FILE, 'w')
    fp.write('NAMES = %r' % utils.NAMES)
    fp.close()
