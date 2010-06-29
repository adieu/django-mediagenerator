from django.conf import settings
from mediagenerator.base import Filter, FileFilter
from pyvascript.grammar import compile
import os

class PyvaScript(Filter):
    def __init__(self, **kwargs):
        super(PyvaScript, self).__init__(**kwargs)
        self.file_filter = PyvaScriptFileFilter

    def get_output(self, variation):
        for input in self.get_input(variation):
            yield input

class PyvaScriptFileFilter(FileFilter):
    def convert(self, content):
        return compile(content)
