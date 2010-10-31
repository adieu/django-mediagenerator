from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
)

if settings.MEDIA_DEV_MODE:
    # Generate media on-the-fly
    from mediagenerator.urls import urlpatterns as mediaurls
    urlpatterns += mediaurls
