from django.conf import settings
from django.conf.urls.defaults import *
import os
import re

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
)

if settings.MEDIA_DEV_MODE:
    from mediagenerator.urls import urlpatterns as mediaurls
    urlpatterns += mediaurls
elif settings.DEBUG:
    path = os.path.join(os.path.dirname(__file__), '_generated_media')
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL),
            'django.views.static.serve',
            {'document_root': path}),
    )
