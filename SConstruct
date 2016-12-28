#!/usr/bin/env python
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

import os

name = 'asterix-data'

formatDef = 'format.rnc'

AddOption('--prefix', dest='prefix', type='string', nargs=1,
        action='store', metavar='DIR', default='/usr/local/share',
        help='installation prefix')

env = Environment(PREFIX = GetOption('prefix'))

Decider('content')

def validate(target, source, env):
    """Validate xml files"""

    # check non asci
    cmd = 'python charvalidate.py ' + ' '.join(map(str,source))
    rv = env.Execute(cmd)
    assert rv==0

    # check with template
    cmd = 'jing -c {} '.format(formatDef) + ' '.join(map(str,source))
    rv = env.Execute(cmd)
    assert rv==0

    print
    print 'No errors found.'

def install(target, source, env):
    base = os.path.join("$PREFIX", name)

    # make sure that target directory is empty, create target if necessary
    target = env.subst(base)
    if os.path.exists(target):
        assert os.path.isdir(target), target + " is not a directory!"
        assert os.listdir(target) == [], target + " directory is not empty!"
    else:
        env.Execute(Mkdir(base))

    # copy files
    env.Execute(Copy(base, formatDef))
    xml = os.path.join(base, 'xml')
    env.Execute(Mkdir(xml))
    for i in Glob('xml/*.xml'):
        env.Execute(Copy(xml, i))

# [(target, help, src, cmd)]
targets = [
    ('validate', 'validate xml files', Glob('xml/*.xml'), validate),
    ('install', 'install data to the system (requires root permission)', [], install)
]

Default('validate')

helpString = ''.join(['    scons {} - {}\n'.format(a,b) for (a,b,c,d) in targets])
Help('Type:\n' + helpString)

# define commands
for a,b,c,d in targets:
    env.Command(a, c, d)

