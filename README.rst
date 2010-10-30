django-mediagenerator_ is an asset manager for Django.
With django-mediagenerator you can combine and compress your JS
and CSS files. It also takes care of automatically versioning your
files (including images), so browsers will load an updated version
when you change any of your files. This works by adding a version
hash to the file name. That way you can still use HTTP caches.

An important advantage of the media generator is that it works
in sandboxed hosting environments like App Engine.

With its backend API the media generator allows you to flexibly
add new features and adjust it to your needs. It also comes with
several backends pre-installed. For example, you can use Sass_,
Python (via pyjs_/Pyjamas), and PyvaScript_.

Also, the media generator provides a development mode in which
files don't get combined and compressed. This simplifies debugging
because you can easily see which file contains a bug. Moreover,
some backends add extra debug information in development mode
to further simplify debugging.

Visit the `project site`_ for more information.

Changelog
=============================================================

Version 1.5
-------------------------------------------------------------

This is another staticfiles-compatibility release which is intended to allow for writing reusable open-source apps.

**Upgrade notes:** The CSS URL rewriting scheme has changed. Previously, ``url()`` statements in CSS files were treated similar to "absolute" URLs where the root is ``STATICFILES_URL`` (or ``MEDIA_URL``). This scheme was used because it was consistent with URLs in Sass. Now URLs are treated as relative to the CSS file. So, if the file ``css/style.css`` wants to link to ``img/icon.png`` the URL now has to be ``url(../img/icon.png)``. Previously it was ``url(img/icon.png)``. One way to upgrade to the staticfiles-compatible scheme is to modify your existing URLs.

If you don't want to change your CSS files this there is an alternative, but it's not staticfiles-compatible. Add the following to your settings: ``REWRITE_CSS_URLS_RELATIVE_TO_SOURCE = False``

**Important:** Sass files still use the old scheme (``url(img/icon.png)``) because this is **much** easier to understand and allows for more reusable code, especially when you ``@import`` other Sass modules and those link to images.

* Made CSS URL rewriting system compatible with ``django.contrib.staticfiles``
* Added support for CSS URLs that contain a hash (e.g.: ``url('webfont.svg#webfontmAfNlbV6')``). Thanks to Karl Bowden for the patch!
* Filter backends now have an additional ``self.bundle`` attribute which contains the final bundle name
* Fixed an incompatibility with Django 1.1 and 1.0 (``django.utils.itercompat.product`` isn't available in those releases)
* Fixed ``MediaMiddleware``, so it doesn't cache error responses

Version 1.4
-------------------------------------------------------------

This is a compatibility release which prepares for the new staticfiles feature in Django 1.3.

**Upgrade notes:** Use ``STATICFILES_URL`` instead of ``MEDIA_URL`` from now on. Starting with Django 1.3 this will default to "/static/" instead of "/media/".

* App media should from now on be stored in a folder named "static". You can still use "media" folders, but this might be deprecated in the future (for the sake of having just one standard for reusable apps).
* ``STATICFILES_URL`` must be used instead of ``MEDIA_URL``
* ``STATICFILES_DIRS`` can be used instead of ``GLOBAL_MEDIA_DIRS``
* ``STATICFILES_ROOT`` can be used instead of ``GENERATED_MEDIA_DIR``

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

.. _django-mediagenerator: http://www.allbuttonspressed.com/projects/django-mediagenerator
.. _project site: django-mediagenerator_
.. _Sass: http://sass-lang.com/
.. _pyjs: http://pyjs.org/
.. _PyvaScript: http://www.allbuttonspressed.com/projects/pyvascript
