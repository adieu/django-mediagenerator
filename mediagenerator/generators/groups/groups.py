from mediagenerator.base import Generator

from itertools import product
from mimetypes import guess_type
from .settings import MEDIA_GROUPS
from .utils import _load_root_filter, _get_key

class Groups(Generator):
    def get_output(self):
        for filetype, groups in MEDIA_GROUPS.items():
            for group in groups:
                backend = _load_root_filter(filetype, group)
                variations = backend._get_variations_with_input()
                if not variations:
                    name, content = self.generate_file(backend, group, filetype, {})
                    yield _get_key(filetype, group), name, content
                else:
                    # Generate media files for all variation combinations
                    combinations = product(variations[key]
                                           for key in sorted(variations.keys()))
                    for combination in combinations:
                        variation_map = zip(sorted(variations.keys()), combination)
                        variation = dict(variation_map)
                        name, content = self.generate_file(backend, group, filetype,
                                                           variation, combination)

                        key = _get_key(filetype, group, variation_map)
                        yield key, name, content

    def get_dev_output(self, name):
        filetype, group, combination, path = name.split('/', 3)
        root = _load_root_filter(filetype, group)
        variations = root._get_variations_with_input()
        variation = dict(zip(sorted(variations.keys()), combination.split(':')))
        content = root.get_dev_output(path, variation)
        mimetype = guess_type('x.' + filetype)[0]
        return content, mimetype

    def get_dev_output_names(self):
        for filetype, groups in MEDIA_GROUPS.items():
            for group in groups:
                backend = _load_root_filter(filetype, group)
                variations = backend._get_variations_with_input()
                if not variations:
                    for name, hash in backend.get_dev_output_names({}):
                        url = '%s/%s//%s' % (filetype, group, name)
                        yield _get_key(filetype, group), url, hash
                else:
                    # Generate media files for all variation combinations
                    combinations = product(variations[key]
                                           for key in sorted(variations.keys()))
                    for combination in combinations:
                        variation_map = zip(sorted(variations.keys()), combination)
                        variation = dict(variation_map)
                        for name, hash in backend.get_dev_output_names(variation):
                            url = '%s/%s/%s/%s' % (filetype, group, combination, name)
                            yield _get_key(filetype, group, variation_map), url, hash

    def generate_file(self, backend, group, filetype, variation, combination=()):
        print 'Generating %s.%s with variation %r' % (group, filetype, variation)
        output = list(backend.get_output(variation))
        if len(output) == 0:
            output = ('',)
        assert len(output) == 1, \
            'Media group "%s" would result in multiple output files' % group
        content = output[0]

        combination = '-'.join(combination)
        if combination:
            combination = '-' + combination
        filename = '%s%s.%s' % (group, combination, filetype)
        return filename, content
