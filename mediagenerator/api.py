from . import settings as media_settings
from .settings import GENERATED_MEDIA_DIR, MEDIA_GENERATORS
from .utils import load_backend, NAMES
import os
import shutil

def generate_media():
    if os.path.exists(GENERATED_MEDIA_DIR):
        shutil.rmtree(GENERATED_MEDIA_DIR)

    # This will make media_url() generate production URLs
    was_dev_mode = media_settings.MEDIA_DEV_MODE
    media_settings.MEDIA_DEV_MODE = False

    NAMES.clear()

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
            fp.write(content)
            fp.close()

            NAMES[key] = url

    media_settings.MEDIA_DEV_MODE = was_dev_mode

    # Generate a module with media file name mappings
    fp = open('_generated_media_names.py', 'w')
    fp.write('NAMES = %r' % NAMES)
    fp.close()
