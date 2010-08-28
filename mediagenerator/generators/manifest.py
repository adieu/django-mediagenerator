from django.conf import settings
from django.template.loader import render_to_string
from mediagenerator.base import Generator
from mediagenerator.utils import get_media_mapping

OFFLINE_MANIFEST = getattr(settings, 'OFFLINE_MANIFEST', {})
if isinstance(OFFLINE_MANIFEST, basestring):
    OFFLINE_MANIFEST = {OFFLINE_MANIFEST: '*'}

def get_tuple(data, name, default=()):
    result = data.get(name, default)
    if isinstance(result, basestring):
        return (result,)
    return result

class Manifest(Generator):
    def generate_version(self, key, url, content):
        return None

    def get_dev_output(self, name):
        config = OFFLINE_MANIFEST[name]
        if isinstance(config, (tuple, list)):
            config = {'cache': config}
        elif isinstance(config, basestring):
            config = {'cache': (config,)}

        cache = tuple(get_tuple(config, 'cache', '*'))
        if cache == ('*',):
            cache = get_media_mapping().keys()
        cache = set(cache) - set(OFFLINE_MANIFEST.keys())
        cache -= set(get_tuple(config, 'exclude'))

        network = get_tuple(config, 'network')
        fallback = get_tuple(config, 'fallback')

        template = get_tuple(config, 'template') + (
            'mediagenerator/manifest/' + name,
            'mediagenerator/manifest/base.manifest'
        )

        content = render_to_string(template, {
            'cache': cache, 'network': network, 'fallback': fallback,
        })
        return content, 'text/cache-manifest'

    def get_dev_output_names(self):
        for name in OFFLINE_MANIFEST:
            yield name, name, None
