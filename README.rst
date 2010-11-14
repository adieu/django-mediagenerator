django-mediagenerator_ is an asset manager for Django.
With django-mediagenerator you can combine and compress your JS
and CSS files. All files (including images) are versioned, so they
can be efficient cached with far-future expires.

The media generator works in sandboxed environments like App Engine.
It supports Sass_, HTML5 offline manifests,  Jinja2,
Python (via pyjs_/Pyjamas), PyvaScript_, and much more. Visit the
`project site`_ for more information.

What's new in version 1.8
=============================================================

* HTML5 manifest now uses a regex to match included/excluded files
* Added support for scss files
* Fixed Sass ``@import`` tracking for partials

See the ``CHANGELOG.rst`` file for the complete changelog.

.. _django-mediagenerator: http://www.allbuttonspressed.com/projects/django-mediagenerator
.. _project site: django-mediagenerator_
.. _Sass: http://sass-lang.com/
.. _pyjs: http://pyjs.org/
.. _PyvaScript: http://www.allbuttonspressed.com/projects/pyvascript
