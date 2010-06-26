# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.simplejson import dumps
from subprocess import Popen
from os.path import getmtime
import os, codecs, shutil

MEDIA_VERSION = unicode(settings.MEDIA_VERSION)
compressor = os.path.join(os.path.dirname(__file__), '.yuicompressor.jar')
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(__file__)))))
GENERATED_MEDIA = os.path.join(PROJECT_ROOT, '_generated_media')
MEDIA_ROOT = os.path.join(GENERATED_MEDIA, MEDIA_VERSION)

def generatemedia(compressed, silent=False):
    if os.path.exists(MEDIA_ROOT):
        shutil.rmtree(MEDIA_ROOT)

    updatemedia(compressed, silent=silent)

def copy_file(path, generated):
    dirpath = os.path.dirname(generated)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    shutil.copyfile(path, generated)

def compress_file(path, silent=False):
    if path.endswith(('.css', '.js')):
        if not silent:
            print '  Running yuicompressor...',
        try:
            cmd = Popen(['java', '-jar', compressor, path, '-o', path])
            if cmd.wait() == 0:
                if not silent:
                    print '%d bytes' % os.path.getsize(path)
            else:
                print 'Failed!'
        except:
            raise Exception("Failed to execute Java VM. "
                "Please make sure that you have installed Java "
                "and that it's in your PATH.")

def updatemedia(compressed=None, silent=False):
    if 'mediautils' not in settings.INSTALLED_APPS:
        return

    # These are needed for i18n
    from django.http import HttpRequest
    from django.views.i18n import javascript_catalog
    from ragendja.apputils import get_app_dirs

    # Remove unused media versions
    if os.path.exists(GENERATED_MEDIA):
        entries = os.listdir(GENERATED_MEDIA)
        if len(entries) != 1 or MEDIA_VERSION not in entries:
            shutil.rmtree(GENERATED_MEDIA)

    # Remove old media if settings got modified (we can't know if COMBINE_MEDIA
    # was changed)
    mtime = getmtime(os.path.join(PROJECT_ROOT, 'settings.py'))
    for app_path in get_app_dirs().values():
        path = os.path.join(app_path, 'settings.py')
        if os.path.exists(path) and os.path.getmtime(path) > mtime:
            mtime = os.path.getmtime(path)
    if os.path.exists(MEDIA_ROOT) and getmtime(MEDIA_ROOT) <= mtime:
        shutil.rmtree(MEDIA_ROOT)

    if compressed is None:
        compressed = getattr(settings, 'FORCE_COMPRESSED_MEDIA', False)

    # Detect language codes
    if not settings.USE_I18N:
        LANGUAGES = (settings.LANGUAGE_CODE,)
    else:
        LANGUAGES = [code for code, _ in settings.LANGUAGES]

    media_dirs = get_app_dirs('media')
    media_dirs['global'] = os.path.join(PROJECT_ROOT, 'media')
    i18n_dir = os.path.join(PROJECT_ROOT, '.i18n')
    site_data_path = os.path.join(PROJECT_ROOT, '.site_data.js')

    COMBINE_MEDIA = {}
    tocombine = []
    for combined, group in settings.COMBINE_MEDIA.items():
        abspathed_group = []
        for filename in group:
            if filename == '.site_data.js':
                abspathed_group.append(site_data_path)
                continue
            app, filepath = filename.replace('/', os.sep).split(os.sep, 1)
            abspathed_group.append(os.path.abspath(
                os.path.join(media_dirs[app], filepath)))
        if '%(LANGUAGE_CODE)s' in combined:
            # This file uses i18n, so generate a separate file per language.
            # The language data is always added before all other files.
            if not os.path.exists(i18n_dir):
                os.makedirs(i18n_dir)
            for LANGUAGE_CODE in LANGUAGES:
                LANGUAGE_BIDI = LANGUAGE_CODE.split('-')[0] in \
                    settings.LANGUAGES_BIDI
                filename = combined % {'LANGUAGE_CODE': LANGUAGE_CODE}
                filepath = os.path.join(i18n_dir, filename)
                tocombine.append(filepath)
                language_group = [filepath] + abspathed_group
                COMBINE_MEDIA[filename] = language_group
                request = HttpRequest()
                request.GET['language'] = LANGUAGE_CODE
                # Add some JavaScript data
                content = 'var LANGUAGE_CODE = "%s";\n' % LANGUAGE_CODE
                content += 'var LANGUAGE_BIDI = ' + \
                    (LANGUAGE_BIDI and 'true' or 'false') + ';\n'
                content += javascript_catalog(request,
                    packages=settings.INSTALLED_APPS).content
                # The hgettext() function just calls gettext() internally, but
                # it won't get indexed by makemessages.
                content += '\nwindow.hgettext = function(text) { return gettext(text); };\n'
                # Add a similar hngettext() function
                content += 'window.hngettext = function(singular, plural, count) { return ngettext(singular, plural, count); };\n'
                # Check if content changed, so we don't regenerate the i18n
                # file unnecessarily.
                if os.path.exists(filepath):
                    fp = codecs.open(filepath, 'r', 'utf-8')
                    old_content = fp.read()
                    fp.close()
                    if old_content == content:
                        continue
                    if not silent:
                        print 'Updating i18n file %s...' % filename
                else:
                    if not silent:
                        print 'Generating i18n file %s...' % filename
                fp = codecs.open(filepath, 'w', 'utf-8')
                fp.write(content)
                fp.close()
        elif '%(LANGUAGE_DIR)s' in combined:
            # Generate CSS files for both text directions
            for LANGUAGE_DIR in ('ltr', 'rtl'):
                value = {'LANGUAGE_DIR': LANGUAGE_DIR}
                COMBINE_MEDIA[combined % value] = [item % value
                                                   for item in abspathed_group]
        else:
            COMBINE_MEDIA[combined] = abspathed_group
        tocombine.extend(abspathed_group)

    # Remove old i18n files
    if os.path.exists(i18n_dir):
        for filename in os.listdir(i18n_dir):
            if filename not in COMBINE_MEDIA:
                if not silent:
                    print 'Removing i18n file %s...' % filename
                os.remove(os.path.join(i18n_dir, filename))
        if not os.listdir(i18n_dir):
            os.rmdir(i18n_dir)

    # Generate/remove site_data file
    if site_data_path in tocombine:
        content = 'window.site_data = {};'
        content += 'window.site_data.settings = %s;' % dumps({
            'MEDIA_URL': settings.MEDIA_URL
        })
        needs_update = not os.path.exists(site_data_path)
        if not needs_update:
            file = codecs.open(site_data_path, 'r', 'utf-8')
            if content != file.read():
                needs_update = True
            file.close()
        if needs_update:
            file = codecs.open(site_data_path, 'w', 'utf-8')
            file.write(content)
            file.close()
    elif os.path.exists(site_data_path):
        os.remove(site_data_path)

    # Remove old generated files
    for root, dirs, files in os.walk(MEDIA_ROOT):
        for file in files:
            path = os.path.join(root, file)
            pretty_name = path[len(MEDIA_ROOT)+1:].replace(os.sep, '/')
            app_path = ''
            if '/' in pretty_name:
                app, filepath = pretty_name.split('/', 1)
                if app in media_dirs:
                    app_path = os.path.join(media_dirs[app], filepath)
            # JavaScript and css files are never copied automatically.
            # You must combine them.
            if pretty_name not in COMBINE_MEDIA.keys() and (
                    file.endswith(('.js', '.css') or not app_path or
                    not os.path.exists(app_path))):
                if not silent:
                    print 'Removing %s...' % pretty_name
                os.remove(path)

    # First, copy all media files that don't need to be combined.
    # We ignore js and css files. They must always be combined.
    for app, media_dir in media_dirs.items():
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                if file.startswith('.') or file.endswith(('.js', '.css')):
                    continue
                path = os.path.join(root, file)
                base = app + path[len(media_dir):]
                generated = os.path.join(MEDIA_ROOT, base)
                # Only overwrite files if they've been modified. Also, only
                # copy files that won't get combined.
                if (path in tocombine or (os.path.exists(generated) and
                        getmtime(generated) >= getmtime(path))):
                    continue
                if not silent:
                    print 'Copying %s...' % base.replace(os.sep, '/')
                copy_file(path, generated)
                if compressed:
                    compress_file(generated, silent=silent)

    # Now combine media files.
    for combined, group in COMBINE_MEDIA.items():
        path = os.path.join(MEDIA_ROOT, combined.replace('/', os.sep))
        # Only overwrite files if they've been modified
        if os.path.exists(path):
            combined_mtime = getmtime(path)
            if not [1 for name in group if os.path.exists(name) and
                                           getmtime(name) >= combined_mtime]:
                continue
        if not silent:
            print 'Combining %s...' % combined
        dirpath = os.path.dirname(path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        cfp = codecs.open(path, 'w', 'utf-8')
        for filename in group:
            try:
                fp = codecs.open(filename, 'r', 'utf-8')
                data = fp.read().lstrip(codecs.BOM_UTF8.decode('utf-8'))
            except:
                print 'Error in %s', filename
                raise
            cfp.write(data)
            cfp.write('\n')
            fp.close()
        cfp.close()
        if compressed:
            compress_file(path)
