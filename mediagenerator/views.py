from django.conf import settings
from django.http import Http404, HttpResponse
from pyvascript.grammar import compile
import os, logging

def serve(request, path, base_path):
    try:
        with open(os.path.join(base_path, path), 'r') as fp:
            content = compile(fp.read())
    except IOError:
        raise Http404
    return HttpResponse(content, content_type='text/javascript')
