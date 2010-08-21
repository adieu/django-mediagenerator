from .utils import _refresh_dev_names, _backend_mapping
from django.http import HttpResponse
from django.utils.cache import patch_cache_control

def serve_dev_mode(request, filename):
    _refresh_dev_names()
    backend = _backend_mapping[filename]
    content, mimetype = backend.get_dev_output(filename)
    response = HttpResponse(content, content_type=mimetype)
    # Cache manifest files MUST NEVER be cached or you'll be unable to update
    # your cached app!!!
    if mimetype != 'text/cache-manifest':
        patch_cache_control(response, private=True, max_age=60*60*24*365)
    return response
