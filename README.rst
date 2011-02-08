Improve your user experience with amazingly fast page loads by combining,
compressing, and versioning your JavaScript & CSS files and images.
Eliminate unnecessary HTTP requests and maximize cache usage with
the django-mediagenerator_ asset manager.

Supports App Engine, Sass_, HTML5 offline manifests,  Jinja2_,
Python/pyjs_, CoffeeScript_, and much more. Visit the
`project site`_ for more information.

Most important changes in version 1.9 - 1.9.2
=============================================================

* Added CoffeeScript support (use ``.coffee`` extension). Contributed by Andrew Allen.
* In cache manifests the ``NETWORK`` section now contains "``*``" by default
* Fixed relative imports in Sass filter
* Fixed i18n filter in development mode. Contributed by Simon Payne.
* Added missing ``base.manifest`` to zip package

See `CHANGELOG.rst`_ for the complete changelog.

.. _django-mediagenerator: http://www.allbuttonspressed.com/projects/django-mediagenerator
.. _project site: django-mediagenerator_
.. _Sass: http://sass-lang.com/
.. _pyjs: http://pyjs.org/
.. _CoffeeScript: http://coffeescript.org/
.. _Jinja2: http://jinja.pocoo.org/
.. _CHANGELOG.rst: https://bitbucket.org/wkornewald/django-mediagenerator/src/tip/CHANGELOG.rst
