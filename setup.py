from setuptools import setup, find_packages

DESCRIPTION = 'Extensible JavaScript/CSS combiner and compressor'

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

setup(name='django-mediagenerator',
      version='0.5',
      packages=find_packages(exclude=('tests', 'tests.*',
                                      'base_project', 'base_project.*')),
      author='Waldemar Kornewald',
      url='http://www.allbuttonspressed.com/projects/django-mediagenerator',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      platforms=['any'],
)
