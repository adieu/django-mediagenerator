from django.conf import settings
import os

PRODUCTION_MEDIA_URL = getattr(settings, 'PRODUCTION_MEDIA_URL', settings.MEDIA_URL)

MEDIA_GENERATORS = getattr(settings, 'MEDIA_GENERATORS', (
#    'mediagenerator.generators.sprites.Sprites',
    'mediagenerator.generators.copyfiles.CopyFiles',
    'mediagenerator.generators.groups.Groups',
))

GENERATED_MEDIA_DIR = os.path.abspath(getattr(settings, 'GENERATE_MEDIA_DIR',
    '_generated_media'))

GLOBAL_MEDIA_DIRS = getattr(settings, 'GLOBAL_MEDIA_DIRS', ())

MEDIA_DEV_MODE = getattr(settings, 'MEDIA_DEV_MODE', settings.DEBUG)
