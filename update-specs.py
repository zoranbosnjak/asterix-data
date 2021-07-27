#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# By Zoran Bošnjak <zoran.bosnjak@sloveniacontrol.si>

# Convert from asterix-specs JSON to XML.

import os
import argparse
import json
import hashlib
import urllib.request

import render.xml

# Path to default upstream repository
upstream_repo = 'https://zoranbosnjak.github.io/asterix-specs'

def download_url(path):
    print('loading', path)
    with urllib.request.urlopen(upstream_repo + path) as url:
        return url.read()

def read_file(path):
    print('reading', path)
    with open(path, 'rb') as f:
        return f.read()

def load_jsons(paths):

    # load from url
    if paths is None:
        manifest = download_url('/manifest.json').decode()
        listing = []
        for spec in json.loads(manifest):
            cat = spec['category']
            for edition in spec['cats']:
                listing.append('/specs/cat{}/cats/cat{}/definition.json'.format(cat, edition))
            for edition in spec['refs']:
                listing.append('/specs/cat{}/refs/ref{}/definition.json'.format(cat, edition))
        return [download_url(i) for i in listing]

    # load from disk
    else:
        listing = []
        for path in paths:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for i in files:
                        (a,b) = os.path.splitext(i)
                        if (a,b) != ('definition', '.json'):
                            continue
                        listing.append(os.path.join(root, i))
            elif os.path.isfile(path):
                listing.append(path)
            else:
                raise Exception('unexpected path type: {}'.path)
        return [read_file(f) for f in listing]

# main
parser = argparse.ArgumentParser(description='Update XML definitions from asterix-specs')
parser.add_argument('--src', metavar='SRC', action='append',
    help='json spec file(s), use upstream repository in no input is given')
parser.add_argument('dst', metavar='DST', help='path to xml output')

args = parser.parse_args()

jsons = load_jsons(args.src)

for s in jsons:
    cks = hashlib.sha1(s).hexdigest()
    root = json.loads(s)
    if root['type'] != 'Basic':
        continue
    cat = root['number']
    edition = root['edition']
    out = 'cat{:03d}_{}.{}.xml'.format(cat, edition['major'], edition['minor'])
    out = os.path.join(args.dst, out)

    os.makedirs(args.dst, exist_ok=True)
    result = render.xml.render(root, cks)
    with open(out, 'w') as f:
        print('writing', out)
        f.write(result)
