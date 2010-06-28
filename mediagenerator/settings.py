import os.path
from django.conf import settings
import os

ROOT_MEDIA_FILTER = getattr(settings, 'ROOT_MEDIA_FILTER', 'mediagenerator.filters.concat.ConcatFilter')

GENERATE_MEDIA = getattr(settings, 'GENERATE_MEDIA', {})

GENERATE_MEDIA_DIR = os.path.abspath(getattr(settings, 'GENERATE_MEDIA_DIR', '_generated_media'))

GLOBAL_MEDIA_DIRS = getattr(settings, 'GLOBAL_MEDIA_DIRS', ())

COPY_MEDIA_FILETYPES = getattr(settings, 'COPY_MEDIA_FILETYPES',
    ('gif', 'jpg', 'jpeg', 'png', 'svg'))
