Changelog
=============================================================

Version 1.9.2
-------------------------------------------------------------

* Added missing ``base.manifest`` template and ``base_project`` to zip package

Version 1.9.1
-------------------------------------------------------------

* Fixed relative imports in Sass filter

Version 1.9
-------------------------------------------------------------

* Added CoffeeScript support (use ``.coffee`` extension). Contributed by Andrew Allen.
* Added caching for CoffeeScript compilation results
* In cache manifests the ``NETWORK`` section now contains "``*``" by default
* By default ``.woff`` files are now copied, too
* Fixed first-time media generation when ``MEDIA_DEV_MODE=False``
* Fixed i18n filter in development mode. Contributed by Simon Payne.
* Fixed support for "/" in bundle names in dev mode (always worked fine in production)
* Changed ``DEV_MEDIA_URL`` fallback from ``STATICFILES_URL`` to ``STATIC_URL`` (has been changed in Django trunk)

Version 1.8
-------------------------------------------------------------

* HTML5 manifest now uses a regex to match included/excluded files
* Added support for scss files
* Fixed Sass ``@import`` tracking for partials

Version 1.7
-------------------------------------------------------------

* Large performance improvements, in particular on App Engine dev_appserver

Version 1.6.1
-------------------------------------------------------------

* Fixed support for Django 1.1 which imports ``mediagenerator.templatetags.media`` as ``django.templatetags.media`` and thus breaks relative imports

Version 1.6
-------------------------------------------------------------

**Upgrade notes:** The installation got simplified. Please remove the media code from your urls.py. The ``MediaMiddleware`` now takes care of everything.

* Added support for CSS data URIs. Doesn't yet generate MHTML for IE6/7 support.
* Added support for pre-bundling i18n JavaScript translations, so you don't need to use Django's slower AJAX view. With this filter translations are part of your generated JS bundle.
* Added support for CleverCSS
* Simplified installation process. The media view got completely replaced by ``MediaMiddleware``.
* Fixed support for output variations (needed by i18n filter to generate the same JS file in different variations for each language)

Version 1.5.1
-------------------------------------------------------------

**Upgrade notes:** There's a conflict with ``STATICFILES_URL`` in Django trunk (1.3). Use ``DEV_MEDIA_URL`` instead from now on.

* ``DEV_MEDIA_URL`` should be used instead of ``MEDIA_URL`` and ``STATICFILES_URL``, though the other two are still valid for backwards-compatibility

Version 1.5
-------------------------------------------------------------

This is another staticfiles-compatibility release which is intended to allow for writing reusable open-source apps.

**Upgrade notes:** The CSS URL rewriting scheme has changed. Previously, ``url()`` statements in CSS files were treated similar to "absolute" URLs where the root is ``STATICFILES_URL`` (or ``MEDIA_URL``). This scheme was used because it was consistent with URLs in Sass. Now URLs are treated as relative to the CSS file. So, if the file ``css/style.css`` wants to link to ``img/icon.png`` the URL now has to be ``url(../img/icon.png)``. Previously it was ``url(img/icon.png)``. One way to upgrade to the staticfiles-compatible scheme is to modify your existing URLs.

If you don't want to change your CSS files there is an alternative, but it's not staticfiles-compatible. Add the following to your settings: ``REWRITE_CSS_URLS_RELATIVE_TO_SOURCE = False``

**Important:** Sass files still use the old scheme (``url(img/icon.png)``) because this is **much** easier to understand and allows for more reusable code, especially when you ``@import`` other Sass modules and those link to images.

* Made CSS URL rewriting system compatible with ``django.contrib.staticfiles``
* Added support for CSS URLs that contain a hash (e.g.: ``url('webfont.svg#webfontmAfNlbV6')``). Thanks to Karl Bowden for the patch!
* Filter backends now have an additional ``self.bundle`` attribute which contains the final bundle name
* Fixed an incompatibility with Django 1.1 and 1.0 (``django.utils.itercompat.product`` isn't available in those releases)
* Fixed ``MediaMiddleware``, so it doesn't cache error responses

Version 1.4
-------------------------------------------------------------

This is a compatibility release which prepares for the new staticfiles feature in Django 1.3.

**Upgrade notes:** Place your app media in a "static" folder instead of a "media" folder. Use ``DEV_MEDIA_URL`` (edit: was ``STATICFILES_URL``) instead of ``MEDIA_URL`` from now on.

* App media is now searched in "static" folders instead of "media". For now, you can still use "media" folders, but this might be deprecated in the future (for the sake of having just one standard for reusable apps).
* ``DEV_MEDIA_URL`` (edit: was ``STATICFILES_URL``) should be used instead of ``MEDIA_URL`` because the meaning of that variable has changed in Django 1.3.
* ``DEV_MEDIA_URL`` falls back to ``STATICFILES_URL`` and ``GLOBAL_MEDIA_DIRS`` falls back to ``STATICFILES_DIRS`` if undefined (you should still use the former, respectively; this is just for convenience)

Version 1.3.1
-------------------------------------------------------------

* Improved handling of media variations. This also fixes a bug with using CSS media types in production mode

Version 1.3
-------------------------------------------------------------

* Added support for setting media type for CSS. E.g.: ``{% include_media 'bundle.css' media='print' %}``

Version 1.2.1
-------------------------------------------------------------

* Fixed caching problems on runserver when using i18n and ``LocaleMiddleware``

Version 1.2
-------------------------------------------------------------

**Upgrade notes:** Please add ``'mediagenerator.middleware.MediaMiddleware'`` as the **first** middleware in your settings.py.

* Got rid of unnecessary HTTP roundtrips when ``USE_ETAGS = True``
* Added Django template filter (by default only used for .html files), contributed by Matt Bierner
* Added media_url() filter which provides access to generated URLs from JS
* CopyFiles backend can now ignore files matching certain regex patterns

Version 1.1
-------------------------------------------------------------

* Added Closure compiler backend
* Added HTML5 cache manifest file backend
* Fixed Sass support on Linux
* Updated pyjs filter to latest pyjs repo version
* "swf" and "ico" files are now copied, too, by default
