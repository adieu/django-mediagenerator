from ...filters import sass
from ...utils import get_media_dirs
from django.conf import settings
from django.core.management.base import NoArgsCommand
from subprocess import Popen, PIPE
import os
import shutil
import sys
import __main__

_frameworks_dir = 'imported-sass-frameworks'
if hasattr(__main__, '__file__'):
    _root = os.path.dirname(__main__.__file__)
    _frameworks_dir = os.path.join(_root, _frameworks_dir)
FRAMEWORKS_DIR = getattr(settings, 'IMPORTED_SASS_FRAMEWORKS_DIR',
                         _frameworks_dir)
FRAMEWORKS_DIR = os.path.normcase(os.path.abspath(FRAMEWORKS_DIR))

PATHS_SCRIPT = os.path.join(os.path.dirname(sass.__file__), 'sass_paths.rb')

def copy_children(src, dst):
    for item in os.listdir(src):
        path = os.path.join(src, item)
        copy_fs_node(path, dst)

def copy_fs_node(src, dst):
    basename = os.path.basename(src)
    dst = os.path.join(dst, basename)
    if os.path.isfile(src):
        shutil.copy(src, dst)
    elif os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        raise ValueError("Don't know how to copy file system node: %s" % src)

class Command(NoArgsCommand):
    help = 'Copies Sass/Compass frameworks into the current project.'

    requires_model_validation = False

    def handle_noargs(self, **options):
        if os.path.exists(FRAMEWORKS_DIR):
            shutil.rmtree(FRAMEWORKS_DIR)
        os.mkdir(FRAMEWORKS_DIR)
        for path in self.get_framework_paths():
            copy_children(path, FRAMEWORKS_DIR)

        if FRAMEWORKS_DIR not in get_media_dirs():
            sys.stderr.write('Please add the "%(dir)s" '
                             'folder to your GLOBAL_MEDIA_DIRS setting '
                             'like this:\n\n'
                             'GLOBAL_MEDIA_DIRS = (\n'
                             '    ...\n'
                             "    os.path.join(os.path.dirname(__file__),\n"
                             "                 '%(dir)s'),\n"
                             "    ...\n"
                             ")\n" % {'dir': os.path.basename(FRAMEWORKS_DIR)})

    def get_framework_paths(self):
        run = ['ruby', PATHS_SCRIPT]
        run.extend(sass.SASS_FRAMEWORKS)
        try:
            cmd = Popen(run, universal_newlines=True,
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, error = cmd.communicate()
            assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
            return map(os.path.abspath, filter(None, output.split('\n')))
        except Exception, e:
            raise ValueError("Failed to execute an internal Ruby script. "
                "Please make sure that you have installed Ruby "
                "(http://ruby-lang.org), Sass (http://sass-lang.com), and "
                "Compass (http://compass-style.org).\n"
                "Error was: %s" % e)
