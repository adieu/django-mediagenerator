from .settings import ROOT_MEDIA_FILTERS, MEDIA_GROUPS, BASE_ROOT_MEDIA_FILTERS
from mediagenerator.utils import load_backend
import os

_cache = {}

def _load_root_filter(group):
    if group not in _cache:
        _cache[group] = _load_root_filter_uncached(group)
    return _cache[group]

def _get_root_filters_list(filetype):
    root_filters = ()
    filetypes = (filetype, '*')
    for filters_spec in (ROOT_MEDIA_FILTERS, BASE_ROOT_MEDIA_FILTERS):
        for filetype in filetypes:
            filters = filters_spec.get(filetype, ())
            if not isinstance(filters, (tuple, list)):
                filters = (filters, )
            root_filters += tuple(filters)
    return root_filters

def _load_root_filter_uncached(group):
    for items in MEDIA_GROUPS:
        if items[0] == group:
            input = items[1:]
            break
    else:
        raise ValueError('Could not find media group "%s"' % group)
    filetype = os.path.splitext(group)[-1].lstrip('.')
    root_filters = _get_root_filters_list(filetype)
    backend_class = load_backend(root_filters[-1])
    for filter in reversed(root_filters[:-1]):
        input = [{'filter': filter, 'input': input,}]

    return backend_class(filter=root_filters[-1], filetype=filetype, input=input)

def _get_key(group, variation_map=None):
    if variation_map:
        group += '?' + '&'.join('='.join(item) for item in variation_map)
    return group
