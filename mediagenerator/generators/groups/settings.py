from django.conf import settings

DEFAULT_MEDIA_FILTERS = getattr(settings, 'DEFAULT_MEDIA_FILTERS', {
    'sass': 'mediagenerator.filters.sass.Sass',
    'py': 'mediagenerator.filters.pyjs_filter.Pyjs',
    'pyva': 'mediagenerator.filters.pyvascript_filter.PyvaScript',
})

ROOT_MEDIA_FILTERS = getattr(settings, 'ROOT_MEDIA_FILTERS', {})

# These are applied in addiiton to ROOT_MEDIA_FILTERS.
# The separation is done because we don't want users to
# always specify the default filters when they merely want
# to configure YUICompressor or Closure.
BASE_ROOT_MEDIA_FILTERS = getattr(settings, 'BASE_ROOT_MEDIA_FILTERS', {
    '*': 'mediagenerator.filters.concat.Concat',
    'css': 'mediagenerator.filters.cssurl.CSSURL',
})

MEDIA_GROUPS = getattr(settings, 'MEDIA_GROUPS', ())
