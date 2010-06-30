from django.http import Http404, HttpResponse
from mimetypes import guess_type

from .settings import GENERATE_MEDIA, ROOT_MEDIA_FILTER
from .utils import _load_root_filter

_cache = {}

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
