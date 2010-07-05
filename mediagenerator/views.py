from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from .utils import _refresh_dev_names, _backend_mapping

@cache_control(private=True, max_age=60*60*24*365)
def serve_dev_mode(request, filename):
    _refresh_dev_names()
    backend = _backend_mapping[filename]
    content, mimetype = backend.get_dev_output(filename)
    return HttpResponse(content, content_type=mimetype)
