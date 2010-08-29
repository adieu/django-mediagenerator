from .settings import ROOT_MEDIA_FILTERS, MEDIA_BUNDLES, BASE_ROOT_MEDIA_FILTERS
from django.conf import settings
from mediagenerator.settings import MEDIA_DEV_MODE
from mediagenerator.utils import load_backend, _refresh_dev_names, \
    _generated_names, media_url
import os

_cache = {}

def _load_root_filter(bundle):
    if bundle not in _cache:
        _cache[bundle] = _load_root_filter_uncached(bundle)
    return _cache[bundle]

def _get_root_filters_list(filetype):
    root_filters = ()
    filetypes = (filetype, '*')
    for filters_spec in (BASE_ROOT_MEDIA_FILTERS, ROOT_MEDIA_FILTERS):
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

def _render_include_media(bundle, variation):
    if MEDIA_DEV_MODE:
        root = _load_root_filter(bundle)
        variations = root._get_variations_with_input()
        variation_map = [(key, variation[key])
                         for key in sorted(variations.keys())]
        _refresh_dev_names()
        bundle_key = _get_key(bundle, variation_map)
        urls = [settings.MEDIA_URL + key for key in _generated_names[bundle_key]]
    else:
        variation_map = tuple((key, variation[key]) for key in sorted(variation.keys()))
        urls = (media_url(_get_key(bundle, variation_map)),)

    filetype = os.path.splitext(bundle)[-1].lstrip('.')
    if filetype == 'css':
        tag = u'<link rel="stylesheet" type="text/css" href="%s" />'
    elif filetype == 'js':
        tag = u'<script type="text/javascript" src="%s"></script>'
    else:
        raise ValueError("""Don't know how to include file type "%s".""" % filetype)

    return '\n'.join(tag % url for url in urls)
