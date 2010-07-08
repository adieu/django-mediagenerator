from .settings import MEDIA_GROUPS
from .utils import _load_root_filter, _get_key
try:
    from itertools import product
except ImportError:
    from django.utils.itercompat import product
from mediagenerator.base import Generator
from mimetypes import guess_type
import os

class Groups(Generator):
    def get_output(self):
        for items in MEDIA_GROUPS:
            group = items[0]
            backend = _load_root_filter(group)
            variations = backend._get_variations_with_input()
            if not variations:
                name, content = self.generate_file(backend, group, {})
                yield _get_key(group), name, content
            else:
                # Generate media files for all variation combinations
                combinations = product(*(variations[key]
                                         for key in sorted(variations.keys())))
                for combination in combinations:
                    variation_map = zip(sorted(variations.keys()), combination)
                    variation = dict(variation_map)
                    name, content = self.generate_file(backend, group,
                                                       variation, combination)

                    key = _get_key(group, variation_map)
                    yield key, name, content

    def get_dev_output(self, name):
        group_combination, path = name.split('/', 1)
        parts = group_combination.split('--')
        group = parts[0]
        combination = parts[1:]
        root = _load_root_filter(group)
        variations = root._get_variations_with_input()
        variation = dict(zip(sorted(variations.keys()), combination))
        content = root.get_dev_output(path, variation)
        mimetype = guess_type(group)[0]
        return content, mimetype

    def get_dev_output_names(self):
        for items in MEDIA_GROUPS:
            group = items[0]
            backend = _load_root_filter(group)
            variations = backend._get_variations_with_input()
            if not variations:
                for name, hash in backend.get_dev_output_names({}):
                    url = '%s/%s' % (group, name)
                    yield _get_key(group), url, hash
            else:
                # Generate media files for all variation combinations
                combinations = product(*(variations[key]
                                         for key in sorted(variations.keys())))
                for combination in combinations:
                    variation_map = zip(sorted(variations.keys()), combination)
                    variation = dict(variation_map)
                    for name, hash in backend.get_dev_output_names(variation):
                        url = '%s--%s/%s' % (group, '--'.join(combination), name)
                        yield _get_key(group, variation_map), url, hash

    def generate_file(self, backend, group, variation, combination=()):
        print 'Generating %s with variation %r' % (group, variation)
        output = list(backend.get_output(variation))
        if len(output) == 0:
            output = ('',)
        assert len(output) == 1, \
            'Media group "%s" would result in multiple output files' % group
        content = output[0]

        combination = '--'.join(combination)
        if combination:
            combination = '--' + combination

        base, ext = os.path.splitext(group)
        filename = base + combination + ext
        return filename, content
