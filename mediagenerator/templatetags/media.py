from django import template
from urllib import urlencode
from ..settings import MEDIA_DEV_MODE
from ..utils import _media_url, _load_root_filter

register = template.Library()

class MediaNode(template.Node):
    def __init__(self, filetype, group, variation):
        self.filetype = filetype
        self.group = group
        self.variation = variation

    def render(self, context):
        filetype = template.Variable(self.filetype).resolve(context)
        group = template.Variable(self.group).resolve(context)
        variation = {}
        for key, value in self.variation.items():
            variation[key] = template.Variable(value).resolve(context)

        if MEDIA_DEV_MODE:
            variation_data = ''
            if variation:
                variation_data = '?%s' % urlencode(variation)
            root = _load_root_filter(filetype, group)
            urls = ('%s/%s/%s%s' % (filetype, group, url, variation_data)
                    for url in root.get_dev_output_names(variation))
        else:
            from _generated_media_versions import MEDIA_VERSIONS, COPY_VERSIONS
            variation_map = tuple((key, variation[key]) for key in variation)
            urls = (MEDIA_VERSIONS[filetype][(group, variation_map)],)

        code = []
        if filetype == 'css':
            tag = '<link rel="stylesheet" type="text/css" href="%s" />'
        elif filetype == 'js':
            tag = '<script type="text/javascript" src="%s"></script>'
        else:
            raise ValueError("""Don't know how to include file type "%s".""" % filetype)
        for url in urls:
            url = _media_url(url)
            code.append(tag % url)
        return '\n'.join(code)

@register.tag
def include_media(parser, token):
    try:
        contents = token.split_contents()
        filetype = contents[1]
        group = contents[2]
        variation_spec = contents[3:]
        variation = {}
        for item in variation_spec:
            key, value = item.split('=')
            variation[key] = value
    except (ValueError, AssertionError, IndexError):
        raise template.TemplateSyntaxError(
            '%r could not parse the arguments: the first argument must be the '
            'file type ("js" or "css"), the second argument must be the name '
            'of a group in the MEDIA_GROUPS setting, and the following '
            'arguments specify the media variation (if you have any) and must '
            'be of the form key="value"' % contents[0])

    return MediaNode(filetype, group, variation)

@register.filter
def media_url(url):
    return _media_url(url)
