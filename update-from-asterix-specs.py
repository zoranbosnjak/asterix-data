#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import json

parser = argparse.ArgumentParser(description='Update XML definitions from asterix-specs')
parser.add_argument('srcPath', metavar='SRC-PATH', help='path to asterix-specs output')
parser.add_argument('dstPath', metavar='DST-PATH', help='path to xml output')

args = parser.parse_args()

with open(os.path.join(args.srcPath, 'manifest.json')) as f:
    manifest = json.loads(f.read())

for item in manifest:
    n = item['category']

    # cats
    for cat in item['cats']:
        cmd = [
            os.path.join(args.srcPath, 'bin', 'render'),
            '--script',
            'render-json/xml.py',
            'render',
            os.path.join(args.srcPath, 'specs', 'cat'+str(n), 'cats', 'cat'+str(cat), 'definition.json'),
            '>',
            os.path.join(args.dstPath, 'cat'+str(n)+'_'+str(cat)+'.xml')
            ]
        print(' '.join(cmd))

    # refs
    for ref in item['refs']:
        pass

