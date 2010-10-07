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

Version 1.2
-------------------------------------------------------------

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
