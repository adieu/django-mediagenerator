from .. import utils
from ..settings import MEDIA_DEV_MODE
from ..utils import _refresh_dev_names, _generated_names
from django import template
from django.conf import settings
from mediagenerator.generators.groups.utils import _load_root_filter, _get_key
import os

register = template.Library()

class MediaNode(template.Node):
    def __init__(self, group, variation):
        self.group = group
        self.variation = variation

    def render(self, context):
        group = template.Variable(self.group).resolve(context)
        variation = {}
        for key, value in self.variation.items():
            variation[key] = template.Variable(value).resolve(context)

        if MEDIA_DEV_MODE:
            root = _load_root_filter(group)
            variations = root._get_variations_with_input()
            variation_map = [(key, variation[key])
                             for key in sorted(variations.keys())]
            _refresh_dev_names()
            group_key = _get_key(group, variation_map)
            urls = [settings.MEDIA_URL + key for key in _generated_names[group_key]]
        else:
            variation_map = tuple((key, variation[key]) for key in sorted(variation.keys()))
            urls = (utils.media_url(_get_key(group, variation_map)),)

        filetype = os.path.splitext(group)[-1].lstrip('.')
        if filetype == 'css':
            tag = '<link rel="stylesheet" type="text/css" href="%s" />'
        elif filetype == 'js':
            tag = '<script type="text/javascript" src="%s"></script>'
        else:
            raise ValueError("""Don't know how to include file type "%s".""" % filetype)

        code = []
        for url in urls:
            code.append(tag % url)
        return '\n'.join(code)

@register.tag
def include_media(parser, token):
    try:
        contents = token.split_contents()
        group = contents[1]
        variation_spec = contents[2:]
        variation = {}
        for item in variation_spec:
            key, value = item.split('=')
            variation[key] = value
    except (ValueError, AssertionError, IndexError):
        raise template.TemplateSyntaxError(
            '%r could not parse the arguments: the first argument must be the '
            'the name of a group in the MEDIA_GROUPS setting, and the '
            'following arguments specify the media variation (if you have '
            'any) and must be of the form key="value"' % contents[0])

    return MediaNode(group, variation)

@register.simple_tag
def media_url(url):
    return utils.media_url(url)
