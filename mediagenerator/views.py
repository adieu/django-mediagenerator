from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from mimetypes import guess_type

from .utils import _load_root_filter

_cache = {}

def _get_root(filetype, group):
    _cache.setdefault(filetype, {})
    if group not in _cache[filetype]:
         _cache[filetype][group] = _load_root_filter(filetype, group)
    return _cache[filetype][group]

@cache_control(private=True, max_age=60*60*24*365)
def serve_dev_mode(request, filetype, group, path):
    root = _get_root(filetype, group)
    variation = dict(request.GET)
    content = root.get_dev_output(path, variation)
    # TODO: support raw file serving for copied files

    mimetype = guess_type('x.' + filetype)[0]
    return HttpResponse(content, content_type=mimetype)

@cache_control(private=True, max_age=60*60*24*365)
def serve_dev_combined_mode(request, filetype, group):
    root = _get_root(filetype, group)
    variation = dict(request.GET)
    files = []
    for name in root.get_dev_output_names(variation):
        files.append(root.get_dev_output(name, variation))
    content = '\n\n'.join(files)
    # TODO: support raw file serving for copied files

    mimetype = guess_type('x.' + filetype)[0]
    return HttpResponse(content, content_type=mimetype)
