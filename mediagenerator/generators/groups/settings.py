from django.conf import settings

DEFAULT_MEDIA_FILTERS = getattr(settings, 'DEFAULT_MEDIA_FILTERS', {
    'sass': 'mediagenerator.filters.sass.Sass',
    'py': 'mediagenerator.filters.pyjs_filter.Pyjs',
    'pyva': 'mediagenerator.filters.pyvascript_filter.PyvaScript',
})

ROOT_MEDIA_FILTERS = getattr(settings, 'ROOT_MEDIA_FILTERS', {})

MEDIA_GROUPS = getattr(settings, 'MEDIA_GROUPS', ())

REWRITE_CSS_MEDIA_URLS = getattr(settings, 'REWRITE_CSS_MEDIA_URLS', True)

CONCAT_MEDIA_FILTER = getattr(settings, 'CONCAT_MEDIA_FILTER',
                              'mediagenerator.filters.concat.Concat')
CSS_URL_MEDIA_FILTER = getattr(settings, 'CSS_URL_MEDIA_FILTER',
                               'mediagenerator.filters.cssurl.CSSURL')
