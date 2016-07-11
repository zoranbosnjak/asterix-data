#! /usr/bin/env python
# -*- coding: utf-8 -*- 

#   Copyright (c) 2016 Sloveniacontrol Ltd. (www.sloveniacontrol.si)

#   This file is part of asterix-data.
#
#   asterix-data is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   asterix-data is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with asterix-data.  If not, see <http://www.gnu.org/licenses/>.

#   Author:
#       Zoran Bošnjak, Sloveniacontrol Ltd.
#           <zoran.bosnjak@sloveniacontrol.si>

"""Find non ascii and tab characters in input files (validator)
"""

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

