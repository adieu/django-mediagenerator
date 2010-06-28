from django.http import Http404, HttpResponse
from .settings import GENERATE_MEDIA, ROOT_MEDIA_FILTER

def serve(request, path):
    backend_class = _load_backend(ROOT_MEDIA_FILTER)
    try:
        ext = path.rsplit('.', 1)[-1]
        if ext in GENERATE_MEDIA:
            for name in sorted(GENERATE_MEDIA[ext].keys(), reverse=True):
                if not path.startswith(name + '/'):
                    continue

                input = GENERATE_MEDIA[ext][name]
                backend = backend_class(filetype=ext, input=input)

                variations = backend._get_variations_with_input()
                if not variations:
                    generate_file(backend, name, filetype, {})
                else:
                    # Generate media files for all variation combinations
                    combinations = product(map(variations.__getitem__, variations.keys()))
                    for combination in combinations:
                        variation = dict(zip(variations.keys(), combination))
                        generate_file(backend, name, filetype, variation, combination)

        # fall back to raw file serving
    except Exception, e:
        raise Http404('Media file not found: %r' % e)
    return HttpResponse(content, content_type='text/javascript')
