#!/usr/bin/env python

import os.path

name = 'asterix-data'
prefix = '/usr/local/share'

formatDef = 'format.rnc'

env = Environment()

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
    base = os.path.join(prefix,name)
    xml = os.path.join(base,'xml')

    env.Execute(Mkdir(base))
    env.Execute(Copy(base, formatDef))

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

