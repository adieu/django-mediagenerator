from hashlib import sha1
from itertools import product
from .settings import MEDIA_GROUPS, GENERATED_MEDIA_DIR, \
    COPY_MEDIA_FILETYPES
from .utils import _load_backend, _load_root_filter, get_media_dirs
import os
import shutil

def generate_file(backend, group, filetype, variation, combination=()):
    print 'Generating %s.%s with variation %r' % (group, filetype, variation)
    output = list(backend.get_output(variation))
    if len(output) == 0:
        output = ('',)
    assert len(output) == 1, \
        'Media group "%s" would result in multiple output files' % group
    output = output[0]

    hash = sha1(output).hexdigest()
    combination += (hash,)
    filename = '%s-%s.%s' % (group, '-'.join(combination), filetype)

    path = os.path.join(GENERATED_MEDIA_DIR, filename)
    parent = os.path.dirname(path)
    if not os.path.exists(parent):
        os.makedirs(parent)
    fp = open(path, 'w')
    fp.write(output)
    fp.close()
    return filename

def generate_media():
    if os.path.exists(GENERATED_MEDIA_DIR):
        shutil.rmtree(GENERATED_MEDIA_DIR)

    generated_files = {}
    for filetype, groups in GENERATE_MEDIA.items():
        for group in groups:
            backend = _load_root_filter(filetype, group)
            variations = backend._get_variations_with_input()
            if not variations:
                generated = generate_file(backend, group, filetype, {})
                generated_files.setdefault(filetype, {})
                generated_files[filetype][(group, ())] = generated
            else:
                # Generate media files for all variation combinations
                combinations = product(variations[key] for key in sorted(variations.keys()))
                for combination in combinations:
                    variation_map = zip(sorted(variations.keys()), combination)
                    variation = dict(variation_map)
                    generated = generate_file(backend, group, filetype,
                                              variation, combination)
                    generated_files.setdefault(filetype, {})
                    generated_files[filetype][(group, variation_map)] = generated

    media_files = {}
    for root in get_media_dirs():
        collect_copyable_files(media_files, root)

    copied_files = {}
    for group, source in media_files.items():
        fp = open(source, 'rb')
        hash = sha1(fp.read()).hexdigest()
        fp.close()

        base, ext = os.path.splitext(group)
        filename = '%s-%s%s' % (base, hash, ext)
        dst = os.path.join(GENERATED_MEDIA_DIR, filename)
        copied_files[group] = filename
        parent = os.path.dirname(dst)
        if not os.path.exists(parent):
            os.makedirs(parent)
        shutil.copyfile(source, dst)

    # Generate a module with versioning information
    fp = open('_generated_media_versions.py', 'w')
    fp.write('MEDIA_VERSIONS = %r\nCOPY_VERSIONS = %r'
             % (generated_files, copied_files))
    fp.close()

def collect_copyable_files(media_files, root):
    # TODO: create a backend/filters API for copyable and binary files
    for root_path, dirs, files in os.walk(root):
        for file in files:
            ext = os.path.splitext(file)[1].lstrip('.')
            if ext in COPY_MEDIA_FILETYPES:
                path = os.path.join(root_path, file)
                media_path = path[len(root)+1:]
                media_files[media_path] = path
