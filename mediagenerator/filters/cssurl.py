from django.conf import settings
from mediagenerator.generators.bundles.base import Filter
from mediagenerator.utils import media_url
import logging
import re

url_re = re.compile(r'url\s*\(["\']?([\w\.][^:]*?)["\']?\)', re.UNICODE)

REWRITE_CSS_MEDIA_URLS = getattr(settings, 'REWRITE_CSS_MEDIA_URLS', True)

class CSSURL(Filter):
    def __init__(self, **kwargs):
        super(CSSURL, self).__init__(**kwargs)
        assert self.filetype == 'css', (
            'CSSURL only supports CSS output. '
            'The parent filter expects "%s".' % self.filetype)

    def get_output(self, variation):
        for input in self.get_input(variation):
            yield self.rewrite_urls(input)

    def get_dev_output(self, name, variation):
        content = super(CSSURL, self).get_dev_output(name, variation)
        return self.rewrite_urls(content)

    def rewrite_urls(self, content):
        if not REWRITE_CSS_MEDIA_URLS:
            return content
        return url_re.sub(self.fixurls, content)

    def fixurls(self, match):
        url = match.group(1)
        if ':' not in url and not url.startswith('/'):
            try:
                url = media_url(url)
            except:
                logging.error('URL not found: %s' % url)
        return 'url(%s)' % url
