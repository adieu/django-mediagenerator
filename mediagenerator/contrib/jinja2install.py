from jinja2 import Environment
from mediagenerator.contrib.jinja2ext import MediaExtension
from mediagenerator.utils import media_url
env = Environment(extensions=[MediaExtension])
env.globals['media_url'] = media_url
