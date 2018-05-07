#!/usr/bin/env python

# Script to re-package unzipped bags as standard transfers, utilizing checksums from bag manifest.
# Assumes bags are structured as either bag/data/(content) or bag/data/objects/(content).
# Enables use of scripts to add metadata to SIP without failing transfer at bag validation.

from __future__ import print_function, unicode_literals

import os
import shutil
import sys


CHECKSUM_ALGOS = set(('md5', 'sha1', 'sha256', 'sha384', 'sha512'))

def manifest_files(path):
    for filename in ['manifest-%s.txt' % a for a in CHECKSUM_ALGOS]:
        f = os.path.join(path, filename)
        if os.path.isfile(f):
            yield f

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def main(transfer_path):
    transfer_path = os.path.abspath(transfer_path)

    # check if transfer is an unzipped bag
    if not os.path.isfile(os.path.join(transfer_path, 'bag-info.txt')):
        return 1
   
    # create metadata and subdoc folders if don't already exist
    data_path = os.path.join(transfer_path, 'data')
    metadata_dir = os.path.join(transfer_path, 'metadata')
    subdoc_dir = os.path.join(metadata_dir, 'submissionDocumentation')
    if not os.path.isdir(metadata_dir):
        os.mkdir(metadata_dir)
    if not os.path.isdir(subdoc_dir):
        os.mkdir(subdoc_dir)

    # move indices, lexicons, and session to metadata folder
    for dir in ['indexes', 'lexicons', 'sessions']:
        os.rename(os.path.join(data_path, 'user', dir), os.path.join(metadata_dir, dir))
    for file in files(os.path.join(data_path, 'user')):
        shutil.move(os.path.join(data_path, 'user', file), metadata_dir)

    # write manifest checksums to checksum file
    for manifest in manifest_files(transfer_path):
        alg = os.path.basename(manifest).replace('manifest-', '').replace('.txt', '')
        with open(os.path.join(transfer_path, manifest), 'r') as old_file:
            with open(os.path.join(metadata_dir, 'checksum.%s' % alg), 'w') as new_file:
                    for line in old_file:
                        if 'data/user/blobs' in line:
                            new_line = line.replace('data/user/blobs', '../objects/user/blobs')
                            new_file.write(new_line)

    # move bag files to submissionDocumentation
    for bag_file in files(transfer_path):
        shutil.move(os.path.join(transfer_path, bag_file), subdoc_dir)

    # move files in data/user/blobs to objects/user/blobs
    objects_dir = os.path.join(transfer_path, 'objects')
    if not os.path.isdir(objects_dir):
        os.mkdir(objects_dir)
    os.rename(os.path.join(data_path), os.path.join(transfer_path, 'objects'))


    return 0



if __name__ == '__main__':
    transfer_path = sys.argv[1]
    sys.exit(main(transfer_path))
