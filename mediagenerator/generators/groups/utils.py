from mediagenerator.utils import load_backend
from .settings import DEFAULT_ROOT_MEDIA_FILTER, ROOT_MEDIA_FILTERS, MEDIA_GROUPS

_cache = {}

def _load_root_filter(filetype, group):
    _cache.setdefault(filetype, {})
    if group not in _cache[filetype]:
         _cache[filetype][group] = _load_root_filter_uncached(filetype, group)
    return _cache[filetype][group]

def _load_root_filter_uncached(filetype, group):
    input = MEDIA_GROUPS[filetype][group]
    root_filter = ROOT_MEDIA_FILTERS.get(filetype, DEFAULT_ROOT_MEDIA_FILTER)
    backend_class = load_backend(root_filter)
    return backend_class(filetype=filetype, input=input)

def _get_key(filetype, group, variation_map=None):
    key = '%s.%s' % (group, filetype)
    if variation_map:
        key += '?' + '&'.join('='.join(item) for item in variation_map)
    return key
