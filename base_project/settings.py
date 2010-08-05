# -*- coding: utf-8 -*-
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

MEDIA_BUNDLES = (
    ('main.css',
        'reset.css',
        'style.css',
    ),
)

# Get project root folder
_project_root = os.path.dirname(__file__)

# Set global media search paths
GLOBAL_MEDIA_DIRS = (
    os.path.join(_project_root, 'media'),
)

# Set media URL (important: don't forget the trailing slash!)
MEDIA_DEV_MODE = DEBUG
PRODUCTION_MEDIA_URL = '/media/'
if MEDIA_DEV_MODE:
    MEDIA_URL = '/devmedia/'
else:
    MEDIA_URL = PRODUCTION_MEDIA_URL

# Configure yuicompressor if available
YUICOMPRESSOR_PATH = os.path.join(
    os.path.dirname(_project_root), 'yuicompressor.jar')
if os.path.exists(YUICOMPRESSOR_PATH):
    ROOT_MEDIA_FILTERS = {
        'js': 'mediagenerator.filters.yuicompressor.YUICompressor',
        'css': 'mediagenerator.filters.yuicompressor.YUICompressor',
    }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db',
    }
}

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'

SITE_ID = 4094

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'mediagenerator',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
)

USE_I18N = False

ADMIN_MEDIA_PREFIX = '/media/admin/'

MEDIA_ROOT = os.path.join(_project_root, 'media')

TEMPLATE_DIRS = (os.path.join(_project_root, 'templates'),)

ROOT_URLCONF = 'urls'

try:
    from settings_local import *
except ImportError:
    pass
