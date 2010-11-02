from . import settings as media_settings
from .settings import GLOBAL_MEDIA_DIRS, PRODUCTION_MEDIA_URL, \
    IGNORE_APP_MEDIA_DIRS, MEDIA_GENERATORS, DEV_MEDIA_URL
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
import os
import re

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

class _MatchNothing(object):
    def match(self, content):
        return False

def prepare_patterns(patterns, setting_name):
    """Helper function for patter-matching settings."""
    if isinstance(patterns, basestring):
        patterns = (patterns,)
    if not patterns:
        return _MatchNothing()
    # First validate each pattern individually
    for pattern in patterns:
        try:
            re.compile(pattern, re.U)
        except re.error:
            raise ValueError("""Pattern "%s" can't be compiled """
                             "in %s" % (pattern, setting_name))
    # Now return a combined pattern
    return re.compile('|'.join(patterns), re.U)

def get_media_mapping():
    if media_settings.MEDIA_DEV_MODE:
        return _generated_names
    return NAMES

def get_media_url_mapping():
    if media_settings.MEDIA_DEV_MODE:
        base_url = DEV_MEDIA_URL
    else:
        base_url = PRODUCTION_MEDIA_URL

    mapping = {}
    for key, value in get_media_mapping().items():
        if isinstance(value, basestring):
            value = (value,)
        mapping[key] = [base_url + url for url in value]

    return mapping

def media_url(key, refresh=True):
    if media_settings.MEDIA_DEV_MODE:
        if refresh:
            _refresh_dev_names()
        urls = [DEV_MEDIA_URL + url for url in _generated_names[key]]
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
        if app in IGNORE_APP_MEDIA_DIRS:
            continue
        for name in ('static', 'media'):
            root = os.path.join(os.path.dirname(import_module(app).__file__),
                                name)
            if os.path.isdir(root):
                media_dirs.append(root)
    return media_dirs

def find_file(name, media_dirs=None):
    if media_dirs is None:
        media_dirs = get_media_dirs()
    name = name.replace(os.sep, '/')
    for root in media_dirs:
        for root_path, dirs, files in os.walk(root):
            for file in files:
                path = os.path.join(root_path, file)
                media_path = path[len(root)+1:].replace(os.sep, '/')
                if media_path == name:
                    return path

def load_backend(backend):
    if backend not in _backends_cache:
        module_name, func_name = backend.rsplit('.', 1)
        _backends_cache[backend] = _load_backend(backend)
    return _backends_cache[backend]

def _load_backend(path):
    module_name, attr_name = path.rsplit('.', 1)
    try:
        mod = import_module(module_name)
    except (ImportError, ValueError), e:
        raise ImproperlyConfigured('Error importing backend module %s: "%s"' % (module_name, e))
    try:
        return getattr(mod, attr_name)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" backend' % (module_name, attr_name))
