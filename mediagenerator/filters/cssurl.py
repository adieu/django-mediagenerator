from mediagenerator.generators.groups.base import Filter
from mediagenerator.utils import media_url
import re

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
        return re.sub(r'url\s*\(["\']?([\w\.][^:]*?)["\']?\)', self.fixurls, content)

    def fixurls(self, match):
        url = match.group(1)
        if ':' not in url and not url.startswith('/'):
            url = media_url(url)
        return 'url(%s)' % url
