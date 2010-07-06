from .settings import GENERATED_MEDIA_DIR, MEDIA_GENERATORS
from .utils import load_backend, _generated_names
from hashlib import sha1
import os
import shutil

def generate_media():
    if os.path.exists(GENERATED_MEDIA_DIR):
        shutil.rmtree(GENERATED_MEDIA_DIR)

    for backend_name in MEDIA_GENERATORS:
        backend = load_backend(backend_name)()
        for key, url, content in backend.get_output():
            hash = sha1(content).hexdigest()
            base, ext = os.path.splitext(url)
            url = '%s-%s%s' % (base, hash, ext)

            path = os.path.join(GENERATED_MEDIA_DIR, url)
            parent = os.path.dirname(path)
            if not os.path.exists(parent):
                os.makedirs(parent)

            fp = open(path, 'wb')
            fp.write(content)
            fp.close()

            _generated_names[key] = url

    # Generate a module with media file name mappings
    fp = open('_generated_media_names.py', 'w')
    fp.write('NAMES = %r' % _generated_names)
    fp.close()
