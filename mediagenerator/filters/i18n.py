from django.conf import settings
from mediagenerator.generators.groups.base import Filter
from django.http import HttpRequest
from django.views.i18n import javascript_catalog

if settings.USE_I18N:
    LANGUAGES = [code for code, _ in settings.LANGUAGES]
else:
    LANGUAGES = (settings.LANGUAGE_CODE,)

class I18NFilter(Filter):
    takes_input = False

    def get_variations(self):
        if self.filetype == 'js':
            return {'language': LANGUAGES}
        elif self.filetype == 'css':
            return {'language_direction': ('ltr', 'rtl')}

    def get_output(self, variation):
        if 'language' in variation:
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
        elif 'language_direction' in variation:
            # Generate CSS files for both text directions
            for LANGUAGE_DIR in ('ltr', 'rtl'):
                value = {'LANGUAGE_DIR': LANGUAGE_DIR}
                COMBINE_MEDIA[combined % value] = [item % value
                                                   for item in abspathed_group]
