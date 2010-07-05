from django.conf import settings

DEFAULT_MEDIA_FILTERS = getattr(settings, 'DEFAULT_MEDIA_FILTERS', {
    'sass': 'mediagenerator.filters.sass.Sass',
    'py': 'mediagenerator.filters.pyjs_filter.Pyjs',
    'pyva': 'mediagenerator.filters.pyvascript_filter.PyvaScript',
})

DEFAULT_ROOT_MEDIA_FILTER = getattr(settings, 'DEFAULT_ROOT_MEDIA_FILTER',
    'mediagenerator.filters.concat.Concat')

ROOT_MEDIA_FILTERS = getattr(settings, 'ROOT_MEDIA_FILTERS', {})

MEDIA_GROUPS = getattr(settings, 'MEDIA_GROUPS', {})
