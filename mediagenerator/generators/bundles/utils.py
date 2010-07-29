from .settings import ROOT_MEDIA_FILTERS, MEDIA_BUNDLES, BASE_ROOT_MEDIA_FILTERS
from mediagenerator.utils import load_backend
import os

_cache = {}

def _load_root_filter(bundle):
    if bundle not in _cache:
        _cache[bundle] = _load_root_filter_uncached(bundle)
    return _cache[bundle]

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

def _load_root_filter_uncached(bundle):
    for items in MEDIA_BUNDLES:
        if items[0] == bundle:
            input = items[1:]
            break
    else:
        raise ValueError('Could not find media bundle "%s"' % bundle)
    filetype = os.path.splitext(bundle)[-1].lstrip('.')
    root_filters = _get_root_filters_list(filetype)
    backend_class = load_backend(root_filters[-1])
    for filter in reversed(root_filters[:-1]):
        input = [{'filter': filter, 'input': input,}]

    return backend_class(filter=root_filters[-1], filetype=filetype, input=input)

def _get_key(bundle, variation_map=None):
    if variation_map:
        bundle += '?' + '&'.join('='.join(item) for item in variation_map)
    return bundle
