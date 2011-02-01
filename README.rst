django-mediagenerator_ is an asset manager for Django.
With django-mediagenerator you can combine and compress your JS
and CSS files. All files (including images) are versioned, so they
can be efficiently cached with far-future expires.

The media generator works in sandboxed environments like App Engine.
It supports Sass_, HTML5 offline manifests,  Jinja2,
Python (via pyjs_/Pyjamas), PyvaScript_, and much more. Visit the
`project site`_ for more information.

What's new in version 1.9.1
=============================================================

* Fixed relative imports in Sass filter

What's new in version 1.9
=============================================================

* Added CoffeeScript support (use ``.coffee`` extension). Contributed by Andrew Allen.
* Added caching for CoffeeScript compilation results
* In cache manifests the ``NETWORK`` section now contains "``*``" by default
* By default ``.woff`` files are now copied, too
* Fixed first-time media generation when ``MEDIA_DEV_MODE=False``
* Fixed i18n filter in development mode. Contributed by Simon Payne.
* Fixed support for "/" in bundle names in dev mode (always worked fine in production)
* Changed ``DEV_MEDIA_URL`` fallback from ``STATICFILES_URL`` to ``STATIC_URL`` (has been changed in Django trunk)

See `CHANGELOG.rst`_ for the complete changelog.

.. _django-mediagenerator: http://www.allbuttonspressed.com/projects/django-mediagenerator
.. _project site: django-mediagenerator_
.. _Sass: http://sass-lang.com/
.. _pyjs: http://pyjs.org/
.. _PyvaScript: http://www.allbuttonspressed.com/projects/pyvascript
.. _CHANGELOG.rst: https://bitbucket.org/wkornewald/django-mediagenerator/src/tip/CHANGELOG.rst
