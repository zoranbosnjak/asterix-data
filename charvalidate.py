#! /usr/bin/env python
# -*- coding: utf-8 -*- 

# Find non ascii and tab characters in input files (validator)

import os, sys
import argparse

def check(s):
    """return list of lines, containing problems"""
    lines = s.splitlines()
    lines = map(lambda line: any([ord(c)>127 or c=='\t' for c in line]), lines)
    lines = enumerate(lines, 1)
    problems = filter(lambda (a,b): b, lines)
    return map(lambda (a,b): a, problems)

# main
parser = argparse.ArgumentParser()
parser.add_argument('infile', nargs='+', type=argparse.FileType('r'))
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
args = parser.parse_args()

data = map(lambda x: (x.name, check(x.read())), args.infile)
problems = sum(map(lambda (filename,cnt): len(cnt), data))

if problems:
    print problems, 'lines found (non-ascii or tabs)'
    print '---'

    for filename, err in data:
        if err:
            print filename, 'lines:', err

    sys.exit(1)

print 'OK'

