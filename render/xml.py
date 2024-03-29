#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unicodedata
from itertools import takewhile, dropwhile

def case(msg, val, *cases):
    """'case' statement as a function."""
    for (a,b) in cases:
        if val == a: return b
    raise Exception('unexpected {}: {}'.format(msg, val))

def getNumber(value):
    """Get Natural/Real/Rational number as an object."""
    class Integer:
        def __init__(self, val):
            self.val = val
        def __int__(self):
            return self.val
        def __float__(self):
            return float(self.val)
        def __str__(self):
            return '{}'.format(float(self.val))

    class Div:
        def __init__(self, numerator, denominator):
            self.numerator = numerator
            self.denominator = denominator
        def __float__(self):
            return float(self.numerator) / float(self.denominator)
        def __str__(self):
            return '{}/{}'.format(float(self.numerator), int(self.denominator))

    class Pow:
        def __init__(self, base, exponent):
            self.val = pow(base, exponent)
        def __int__(self):
            return self.val
        def __float__(self):
            return float(self.val)
        def __str__(self):
            return '{}'.format(self.val)

    t = value['type']

    if t == 'Integer':
        val = value['value']
        return Integer(val)
    if t == 'Div':
        x, y = value['numerator'], value['denominator']
        return Div(getNumber(x), getNumber(y))
    if t == 'Pow':
        x, y = value['base'], value['exponent']
        return Pow(x, y)
    raise Exception('unexpected value type {}'.format(t))

def getRule(rule):
    t = rule['type']
    if t == 'ContextFree':
        return rule['value']
    elif t == 'Dependent':
        return rule['default']
    else:
        raise Exception('unexpected type: {}'.format(t))

class Indent(object):
    """Simple indent context manager."""
    def __init__(self):
        self.accumulator = []
        self.indentLevel = 0

    def __enter__(self):
        self.indentLevel += 1

    def __exit__(self, exec_type, exec_val, exec_tb):
        self.indentLevel -= 1

    def tell(self, s):
        s = replaceOutput(s) # This program requires ascii only.
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')
        s = ' '*self.indentLevel*4 + s
        self.accumulator.append(s.rstrip())

def replaceString(s, mapping):
    for (key,val) in mapping.items():
        s = s.replace(key, val)
    return s

def replaceOutput(s):
    return replaceString(s, {
        u'–': '-',
        u'“': '',
        u'”': '',
        u'°': 'deg',
    })

def xmlquote(s):
    return replaceString(s, {
        '"': "&quot;",
        "&": "&amp;",
        "'": "&apos;",
        "<":  "&lt;",
        ">": "&gt;",
    })

def itemLine(item):
    itemType = getRule(item['rule'])['type']
    if itemType != 'Group':
        if itemType == 'Element':
            itemType = 'Fixed'
        return '<item name="{}" type="{}">'.format(item['name'], itemType)
    else:
        return '<item name="{}">'.format(item['name'])

def renderTopItem(indent, item):
    # manipulate 'repetitive fx' item
    variation = getRule(item['rule'])
    if variation['type'] == 'Repetitive' and variation['rep']['type'] == 'Fx':
        var = variation['variation'].copy()
        if var['type'] != 'Element':
            raise Exception("Expecting 'Element'")
        n = var['size']
        item = item.copy()
        rule = {
            'type': 'ContextFree',
            'value': var,
            }
        var2 = {
            'type': 'Extended',
            'first': n+1,
            'extents': n+1,
            'fx': 'Regular',
            'items': [{
                'definition': None,
                'description': None,
                'name': 'Subitem',
                'remark': None,
                'spare': False,
                'title': 'Subitem',
                'rule': rule,
                }]
        }
        item['rule'] = {
            'type': 'ContextFree',
            'value': var2,
            }
    tell = indent.tell
    tell(itemLine(item))
    with indent:
        title = item['title']
        if title:
            tell('<dsc>{}</dsc>'.format(xmlquote(title)))
        renderVariation(indent, getRule(item['rule']))
    tell('</item>')

def ffloat(val):
    val = format(float(val), '.16f')
    val = val.rstrip('0')
    if val[-1] == '.':
        val += '0'
    return val

def split_list(delim, lst):
    if not lst:
        return
    a = list(takewhile(lambda x: x != delim, lst))
    b = list(dropwhile(lambda x: x != delim, lst))[1:]
    yield a
    for i in split_list(delim, b):
        yield i

def recalculate_extended_sizes(lst):
    def size_of(i):
        if i is None:
            return None # FX
        if i['spare']:
            return i['length']
        var = getRule(i['rule'])
        vt = var['type']
        if vt == 'Element':
            return var['size']
        if vt == 'Group':
            return sum([size_of(j) for j in getRule(i['rule'])['items']])
        raise Exception('not a fixed item')
    sizes = list(split_list(None, list(map(size_of, lst))))
    sizes = [sum(i) for i in sizes]
    a = sizes[0] + 1
    b = [i + 1 for i in sizes[1:]]
    if not b:
        b = [8]
    # all extended sizes must be the same and byte aligned
    assert all(lambda x: x==b[0] for x in b)
    b = b[0]
    assert (a % 8) == 0
    assert (b % 8) == 0
    return (a,b)

def renderVariation(indent, variation):
    tell = indent.tell

    def renderInteger(value):
        tell('<convert>')
        with indent:
            sig = '' if value['signed'] else 'unsigned '
            tell('<type>{}</type>'.format(sig + 'integer'))
            for i in value['constraints']:
                if i['type'] in ['>', '>=']:
                    tell('<min>{}</min>'.format(int(getNumber(i['value']))))
                if i['type'] in ['<', '<=']:
                    tell('<max>{}</max>'.format(int(getNumber(i['value']))))
        tell('</convert>')

    def renderQuantity(value):
        tell('<convert>')
        with indent:
            sig = '' if value['signed'] else 'unsigned '
            tell('<type>{}</type>'.format(sig + 'decimal'))
            lsb = getNumber(value['lsb'])
            tell('<lsb>{}</lsb>'.format(lsb))
            unit = value['unit']
            if unit is not None:
                tell('<unit>{}</unit>'.format(unit))

            for i in value['constraints']:
                if i['type'] in ['>', '>=']:
                    tell('<min>{}</min>'.format(float(getNumber(i['value']))))
                if i['type'] in ['<', '<=']:
                    tell('<max>{}</max>'.format(float(getNumber(i['value']))))
        tell('</convert>')

    def renderElement():
        tell('<len>{}</len>'.format(variation['size']))
        content = getRule(variation['rule'])
        t = content['type']
        if t == 'Raw':
            pass
        elif t == 'Table':
            tell('<values>')
            with indent:
                for key,value in content['values']:
                    tell('<value val="{}" dsc="{}"/>'.format(key, xmlquote(value)))
            tell('</values>')
        elif t == 'String':
            f = case('string variatioin', content['variation'],
                ('StringAscii', lambda: tell('<convert><type>string</type></convert>')),
                ('StringICAO', lambda: tell('<convert><type>ACID</type></convert>')),
                ('StringOctal', lambda: None),
                )
            f ()
        elif t == 'Integer':
            renderInteger(content)
        elif t == 'Quantity':
            renderQuantity(content)
        elif t == 'Bds':
            pass
        else:
            raise Exception('unexpected value type {}'.format(t))

    def renderMaybeItem(n, item):
        if item['spare']:
            tell('<item name="spare{}" type="Spare"><len>{}</len></item>'.format(n, item['length']))
            return True
        else:
            tell(itemLine(item))
            with indent:
                title = item['title']
                if title:
                    tell('<dsc>{}</dsc>'.format(xmlquote(title)))
                renderVariation(indent, getRule(item['rule']))
            tell('</item>')
            return False

    def renderGroup():
        tell('<items>')
        with indent:
            spareIndex = 1
            for item in variation['items']:
                isSpare = renderMaybeItem(spareIndex, item)
                if isSpare:
                    spareIndex += 1
        tell('</items>')

    def renderExtended():
        n1, n2 = recalculate_extended_sizes(variation['items'])
        tell('<len>({},{})</len>'.format(n1, n2))
        # render the rest of non-fx items like 'group'
        renderVariation(indent, {
            "type": "Group",
            "items": [i for i in variation['items'] if i is not None]
        })

    def renderRepetitive():
        if variation['rep']['type'] != 'Regular':
            raise Exception('irregular repetitive item')
        if variation['rep']['size'] != 8:
            raise Exception('unexpected repetition size')
        var = variation['variation']
        if var['type'] == 'Element':
            # repetitive type expects additional level
            # so just make a 'Group' with a single item.
            renderVariation(indent, {
                "type": "Group",
                "items": [{
                    "definition": None,
                    "description": None,
                    "name": "item",
                    "remark": None,
                    "spare": False,
                    "title": "title",
                    "rule": {
                        'type': 'ContextFree',
                        'value': var,
                    },
                    }]
            })
        else:
            renderVariation(indent, var)

    def renderExplicit():
        pass

    def renderRfs():
        pass

    def renderCompound():
        tell('<items>')
        with indent:
            spareIndex = 1
            for item in variation['items']:
                if item is None:
                    tell('<item></item>')
                else:
                    isSpare = renderMaybeItem(spareIndex, item)
                    if isSpare:
                        spareIndex += 1
        tell('</items>')

    return locals()['render'+variation['type']]()

def renderUap(indent, uap):
    tell = indent.tell
    ut = uap['type']
    if ut == 'uap':
        variations = [{'name': 'uap', 'items': uap['items']}]
    elif ut == 'uaps':
        variations = uap['variations']
    else:
        raise Exception('unexpected uap type {}'.format(ut))
    tell('<uaps>')
    with indent:
        for var in variations:
            name = var['name']
            tell('<{}>'.format(name))
            with indent:
                for i in var['items']:
                    tell('<item>{}</item>'.format(i or ''))
            tell('</{}>'.format(name))
    tell('</uaps>')

def render(root, cks):
    indent = Indent()
    tell = indent.tell
    category = root['number']
    edition = root['edition']
    tell('<?xml version="1.0" encoding="UTF-8" ?>')
    tell('')
    tell('<!--')
    with indent:
        tell('Do not edit this file directly!')
        tell('')
        tell('This file is auto-generated from json specs file')
        tell('from this project: https://zoranbosnjak.github.io/asterix-specs/')
        tell('See README.md file for details.')
        tell('')
        tell('sha1sum of the json input: {}'.format(cks))
    tell('-->')
    tell('')
    tell('<category cat="{:03d}" edition="{}.{}">'.format(category, edition['major'], edition['minor']))
    with indent:
        tell('<dsc>Asterix Category {:03d}, edition {}.{}</dsc>'.format(category, edition['major'], edition['minor']))
        tell('<items>')
        with indent:
            [renderTopItem(indent, item) for item in root['catalogue']]
        tell('</items>')
    with indent:
        renderUap(indent, root['uap'])
    tell('</category>')
    return ''.join([line+'\n' for line in indent.accumulator])
