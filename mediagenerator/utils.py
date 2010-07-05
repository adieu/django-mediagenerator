from django.conf import settings
from django.utils.importlib import import_module
from .settings import GLOBAL_MEDIA_DIRS, MEDIA_DEV_MODE, \
    PRODUCTION_MEDIA_URL, MEDIA_GENERATORS
import os

try:
    from _generated_media_names import NAMES
except ImportError:
    NAMES = {}

_backends_cache = {}

_generators_cache = []
_generated_names = {}
_backend_mapping = {}

def _load_generators():
    if not _generators_cache:
        for name in MEDIA_GENERATORS:
            backend = load_backend(name)()
            _generators_cache.append(backend)
    return _generators_cache

def _refresh_dev_names():
    _generated_names.clear()
    _backend_mapping.clear()
    for backend in _load_generators():
        for key, url, hash in backend.get_dev_output_names():
            versioned_url = url
            if hash:
                versioned_url += '?version=' + hash
            _generated_names.setdefault(key, [])
            _generated_names[key].append(versioned_url)
            _backend_mapping[url] = backend

def media_url(key, dev_mode=MEDIA_DEV_MODE):
    if dev_mode:
        _refresh_dev_names()
        urls = [settings.MEDIA_URL + url for url in _generated_names[key]]
        if len(urls) == 1:
            return urls[0]
        return urls
    return PRODUCTION_MEDIA_URL + NAMES[key]

def get_media_dirs():
    media_dirs = []
    for root in GLOBAL_MEDIA_DIRS:
        root = os.path.abspath(root)
        if os.path.isdir(root):
            media_dirs.append(root)
    for app in settings.INSTALLED_APPS:
        root = os.path.join(os.path.dirname(import_module(app).__file__), 'media')
        if os.path.isdir(root):
            media_dirs.append(root)
    return media_dirs

def find_file(name):
    name = name.replace(os.sep, '/')
    for root in get_media_dirs():
        for root_path, dirs, files in os.walk(root):
            for file in files:
                path = os.path.join(root_path, file)
                media_path = path[len(root)+1:].replace(os.sep, '/')
                if media_path == name:
                    return path

def load_backend(backend, default_backend=None):
    if backend is None:
        if default_backend is None:
            raise ValueError('No backend provided')
        backend = default_backend
    if backend not in _backends_cache:
        module_name, func_name = backend.rsplit('.', 1)
        _backends_cache[backend] = getattr(import_module(module_name), func_name)
    return _backends_cache[backend]
