#!/usr/bin/env python

# Script to re-package unzipped bags as standard transfers, utilizing checksums from bag manifest.
# Assumes bags are structured as either bag/data/(content) or bag/data/objects/(content).
# Enables use of scripts to add metadata to SIP without failing transfer at bag validation.

from __future__ import print_function, unicode_literals

import os
import shutil
import sys
import glob
import bagit
import hashlib


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
    data_path = os.path.join(transfer_path, 'data')
    objects_path = os.path.join(data_path, 'objects')
    user_path = os.path.join(data_path, 'user')

    # check if transfer is an unzipped bag
    try:
        bag = bagit.Bag(transfer_path)
    except:
        return 1
   

    # move files in data/objects/user/blobs to data/user/blobs
    os.rename(os.path.join(objects_path, 'user'), user_path)

    # move submission docs -> md/submission
    md_path = os.path.join(data_path, 'objects', 'metadata', 'transfers')
    transfer_paths = os.listdir(md_path)
    if len(transfer_paths) != 1:
        return 1
    else:
        md_path = os.path.join(md_path, transfer_paths[0])
    for dir in ['indexes', 'lexicons', 'sessions']:
        os.rename(os.path.join(md_path, dir), os.path.join(user_path, dir))

    
    # delete thumbnails
    thumbnail_path =  os.path.join(data_path, 'thumbnails')
    if os.path.exists(thumbnail_path):
        shutil.rmtree(thumbnail_path)

    # update manifests
    all_keys = list(bag.entries.keys())
    old_user_relpath = os.path.relpath(os.path.join(objects_path, 'user'), transfer_path)
    user_relpath = os.path.join('data/user')
    md_relpath = os.path.relpath(md_path, transfer_path)
    md_relpaths = [os.path.join(md_relpath, dir) for dir in ['indexes', 'lexicons', 'sessions']]

    for key in all_keys:
        if 'thumbnails' in key:
            del bag.entries[key]
        if old_user_relpath in key:
            new_key = key.replace(old_user_relpath, user_relpath)
            bag.entries[new_key] = bag.entries.pop(key)
        for epadd_path in md_relpaths:
            if epadd_path in key:
                new_key = key.replace(md_relpath, user_relpath)
                bag.entries[new_key] = bag.entries.pop(key)

    # write manifest checksums to checksum file
    for manifest in manifest_files(transfer_path):
        alg = os.path.basename(manifest).replace('manifest-', '').replace('.txt', '')
        with open(os.path.join(transfer_path, manifest), 'w') as manifest:
            for payload_file, hashes in bag.entries.items():
                if payload_file.startswith("data" + os.sep):
                    manifest.write("{} {}\n".format(hashes[alg], bagit._encode_filename(payload_file)))
    
    # update 0xum
    total_bytes = 0
    total_files = 0

    for payload_file in bag.payload_files():
        payload_file = os.path.join(bag.path, payload_file)
        total_bytes += os.stat(payload_file).st_size
        total_files += 1

    generated_oxum = "{0}.{1}".format(total_bytes, total_files)
    bag.info["Payload-Oxum"] = generated_oxum
    bagit._make_tag_file(os.path.join(bag.path, "bag-info.txt"), bag.info)


    #bagit._make_tagmanifest_file is not working, kill tag manifest for now
    for file in os.listdir(transfer_path):
        if file.startswith('tagmanifest'):
            os.remove(os.path.join(transfer_path, file))

    return 0


if __name__ == '__main__':
    transfer_path = sys.argv[1]
    sys.exit(main(transfer_path))