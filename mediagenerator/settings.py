from django.conf import settings
import os

DEFAULT_MEDIA_FILTERS = getattr(settings, 'DEFAULT_MEDIA_FILTERS', {
    'sass': 'mediagenerator.filters.sass.Sass',
    'py': 'mediagenerator.filters.pyjs_filter.Pyjs',
    'pyva': 'mediagenerator.filters.pyvascript_filter.PyvaScript',
})

DEFAULT_ROOT_MEDIA_FILTER = getattr(settings, 'DEFAULT_ROOT_MEDIA_FILTER',
    'mediagenerator.filters.concat.Concat')

ROOT_MEDIA_FILTERS = getattr(settings, 'ROOT_MEDIA_FILTERS', {})

MEDIA_GENERATORS = getattr(settings, 'MEDIA_GENERATORS', (
    'mediagenerator.generators.sprites.Sprites',
    'mediagenerator.generators.groups.Groups',
    'mediagenerator.generators.copyfiles.CopyFiles',
))

MEDIA_GROUPS = getattr(settings, 'MEDIA_GROUPS', {})

GENERATED_MEDIA_DIR = os.path.abspath(getattr(settings, 'GENERATE_MEDIA_DIR',
    '_generated_media'))

GLOBAL_MEDIA_DIRS = getattr(settings, 'GLOBAL_MEDIA_DIRS', ())

COPY_MEDIA_FILETYPES = getattr(settings, 'COPY_MEDIA_FILETYPES',
    ('gif', 'jpg', 'jpeg', 'png', 'svg'))

MEDIA_DEV_MODE = getattr(settings, 'MEDIA_DEV_MODE', settings.DEBUG)
