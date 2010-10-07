from .utils import _refresh_dev_names, _backend_mapping
from django.http import HttpResponse, Http404

def serve_dev_mode(request, filename):
    _refresh_dev_names()
    try:
        backend = _backend_mapping[filename]
    except KeyError:
        raise Http404('No such file "%s"' % filename)
    content, mimetype = backend.get_dev_output(filename)
    return HttpResponse(content, content_type=mimetype)
