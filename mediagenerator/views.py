from django.http import Http404, HttpResponse
from mimetypes import guess_type

from .settings import GENERATE_MEDIA, ROOT_MEDIA_FILTER
from .utils import _load_root_filter

def serve(request, filetype, group, path):
    mimetype = guess_type('x.' + filetype)[0]

    try:
        root = _load_root_filter(filetype, group)
        variation = dict(request.GET)
        content = root.get_dev_output(path, variation)
        # TODO: support raw file serving for copied files
    except Exception, e:
        raise Http404('Media file not found: %r' % e)

    return HttpResponse(content, content_type=mimetype)
