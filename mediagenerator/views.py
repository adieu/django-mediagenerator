from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from mimetypes import guess_type

from .utils import _load_root_filter

_cache = {}

@cache_control(private=True, max_age=60*60*24*365)
def serve(request, filetype, group, path):
    mimetype = guess_type('x.' + filetype)[0]

    _cache.setdefault(filetype, {})
    if group not in _cache[filetype]:
        root = _cache[filetype][group] = _load_root_filter(filetype, group)
    else:
        root = _cache[filetype][group]
    variation = dict(request.GET)
    content = root.get_dev_output(path, variation)
    # TODO: support raw file serving for copied files

    return HttpResponse(content, content_type=mimetype)
