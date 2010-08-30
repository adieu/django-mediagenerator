from django.utils.simplejson import dumps
from mediagenerator.generators.bundles.base import Filter
from mediagenerator.utils import get_media_url_mapping
from hashlib import sha1

_CODE = """
_$MEDIA_URLS = %s;

media_urls = function(key) {
  var urls = _$MEDIA_URLS[key];
  if (!urls)
    throw 'Could not resolve media url ' + key;
  return urls;
};

media_url = function(key) {
  var urls = media_urls(key);
  if (urls.length == 1)
    return urls[0];
  return urls;
};
""".lstrip()

class MediaURL(Filter):
    takes_input = False

    def __init__(self, **kwargs):
        super(MediaURL, self).__init__(**kwargs)
        assert self.filetype == 'js', (
            'MediaURL only supports JS output. '
            'The parent filter expects "%s".' % self.filetype)

    def get_output(self, variation):
        yield self._compile()

    def get_dev_output(self, name, variation):
        assert name == '.media_url.js'
        return self._compile()

    def get_dev_output_names(self, variation):
        content = self._compile()
        hash = sha1(content).hexdigest()
        yield '.media_url.js', hash

    def _compile(self):
        return _CODE % dumps(get_media_url_mapping())
