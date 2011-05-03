# -*- coding: utf-8 -*-
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

MEDIA_BUNDLES = (
    ('main.css',
        'css/reset.css',
        'css/style.css',
        'css/icons/icon.css',
    ),
)

# Get project root folder
_project_root = os.path.dirname(__file__)

# Set global media search paths
GLOBAL_MEDIA_DIRS = (
    os.path.join(_project_root, 'static'),
)

# Set media URL (important: don't forget the trailing slash!).
# PRODUCTION_MEDIA_URL is used when running manage.py generatemedia
MEDIA_DEV_MODE = DEBUG
DEV_MEDIA_URL = '/devmedia/'
PRODUCTION_MEDIA_URL = '/media/'

# Configure yuicompressor if available
YUICOMPRESSOR_PATH = os.path.join(
    os.path.dirname(_project_root), 'yuicompressor.jar')
if os.path.exists(YUICOMPRESSOR_PATH):
    ROOT_MEDIA_FILTERS = {
        'js': 'mediagenerator.filters.yuicompressor.YUICompressor',
        'css': 'mediagenerator.filters.yuicompressor.YUICompressor',
    }

ADMIN_MEDIA_PREFIX = '/media/admin/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db',
    }
}

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'

SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'mediagenerator',
)

MIDDLEWARE_CLASSES = (
    'mediagenerator.middleware.MediaMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
)

USE_I18N = False

TEMPLATE_DIRS = (os.path.join(_project_root, 'templates'),)

ROOT_URLCONF = 'urls'
