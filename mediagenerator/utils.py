from django.conf import settings
from django.utils.importlib import import_module
from .settings import GLOBAL_MEDIA_DIRS, ROOT_MEDIA_FILTER, GENERATE_MEDIA
import os

_backends_cache = {}

def _media_url(url):
    return settings.MEDIA_URL + url

def _load_root_filter(filetype, group):
    input = GENERATE_MEDIA[filetype][group]
    backend_class = _load_backend(ROOT_MEDIA_FILTER)
    return backend_class(filetype=filetype, input=input)

def _get_media_dirs():
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

def _find_file(name):
    name = name.replace(os.sep, '/')
    for root in _get_media_dirs():
        for root_path, dirs, files in os.walk(root):
            for file in files:
                path = os.path.join(root_path, file)
                media_path = path[len(root)+1:].replace(os.sep, '/')
                if media_path == name:
                    return path

def _load_backend(backend, default_backend=None):
    if backend is None:
        if default_backend is None:
            raise ValueError('No backend provided')
        backend = default_backend
    if backend not in _backends_cache:
        module_name, func_name = backend.rsplit('.', 1)
        _backends_cache[backend] = getattr(import_module(module_name), func_name)
    return _backends_cache[backend]
