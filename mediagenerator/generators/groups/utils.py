from .settings import DEFAULT_ROOT_MEDIA_FILTER, ROOT_MEDIA_FILTERS, \
    MEDIA_GROUPS
from mediagenerator.utils import load_backend
import os

_cache = {}

def _load_root_filter(group):
    if group not in _cache:
        _cache[group] = _load_root_filter_uncached(group)
    return _cache[group]

def _load_root_filter_uncached(group):
    for items in MEDIA_GROUPS:
        if items[0] == group:
            input = items[1:]
            break
    else:
        raise ValueError('Could not find media group "%s"' % group)
    filetype = os.path.splitext(group)[-1].lstrip('.')
    root_filters = ROOT_MEDIA_FILTERS.get(filetype, DEFAULT_ROOT_MEDIA_FILTER)
    if not isinstance(root_filters, (tuple, list)):
        root_filters = (root_filters, )

    backend_class = load_backend(root_filters[-1])
    for filter in reversed(root_filters[:-1]):
        input = [{'filter': filter, 'input': input,}]

    return backend_class(filter=root_filters[-1], filetype=filetype, input=input)

def _get_key(group, variation_map=None):
    if variation_map:
        group += '?' + '&'.join('='.join(item) for item in variation_map)
    return group
