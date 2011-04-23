Improve your user experience with amazingly fast page loads by combining,
compressing, and versioning your JavaScript & CSS files and images.
django-mediagenerator_ eliminates unnecessary HTTP requests
and maximizes cache usage.

Supports App Engine, Sass_, HTML5 offline manifests,  Jinja2_,
Python/pyjs_, CoffeeScript_, and much more. Visit the
`project site`_ for more information.

Most important changes in version 1.10
=============================================================

* Added Compass support to Sass filter. You now have to install both Compass and Sass. Import Sass/Compass frameworks via ``manage.py importsassframeworks``.
* Fixed CoffeeScript support on OSX
* Fixed support for non-ascii chars in input files

See `CHANGELOG.rst`_ for the complete changelog.

.. _django-mediagenerator: http://www.allbuttonspressed.com/projects/django-mediagenerator
.. _project site: django-mediagenerator_
.. _Sass: http://sass-lang.com/
.. _pyjs: http://pyjs.org/
.. _CoffeeScript: http://coffeescript.org/
.. _Jinja2: http://jinja.pocoo.org/
.. _CHANGELOG.rst: https://bitbucket.org/wkornewald/django-mediagenerator/src/tip/CHANGELOG.rst
