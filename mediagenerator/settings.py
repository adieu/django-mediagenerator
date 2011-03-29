from django.conf import settings
import os
import __main__

default_map_file_path = '_generated_media_names.py'
default_media_dir = '_generated_media'
if hasattr(__main__,"__file__"):# __main__ is not guaranteed to have the __file__ attribute
    default_map_file_path = os.path.join(os.path.dirname(__main__.__file__), default_map_file_path)
    default_media_dir = os.path.join(os.path.dirname(__main__.__file__), default_media_dir)

DEV_MEDIA_URL = getattr(settings, 'DEV_MEDIA_URL',
                        getattr(settings, 'STATIC_URL', settings.MEDIA_URL))
PRODUCTION_MEDIA_URL = getattr(settings, 'PRODUCTION_MEDIA_URL', DEV_MEDIA_URL)

MEDIA_GENERATORS = getattr(settings, 'MEDIA_GENERATORS', (
    'mediagenerator.generators.copyfiles.CopyFiles',
    'mediagenerator.generators.bundles.Bundles',
    'mediagenerator.generators.manifest.Manifest',
))

GENERATED_MEDIA_DIR = os.path.abspath(default_media_dir)

GENERATED_MEDIA_MAP_FILE = os.path.abspath(default_map_file_path)

GLOBAL_MEDIA_DIRS = getattr(settings, 'GLOBAL_MEDIA_DIRS',
                            getattr(settings, 'STATICFILES_DIRS', ()))

IGNORE_APP_MEDIA_DIRS = getattr(settings, 'IGNORE_APP_MEDIA_DIRS',
    ('django.contrib.admin',))

MEDIA_DEV_MODE = getattr(settings, 'MEDIA_DEV_MODE', settings.DEBUG)