#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import hashlib
from formats.common import getNumber, renderRule, case

accumulator = []
indentLevel = 0

class Indent(object):
    """Simple indent context manager."""
    def __enter__(self):
        global indentLevel
        indentLevel += 1
    def __exit__(self, exec_type, exec_val, exec_tb):
        global indentLevel
        indentLevel -= 1

indent = Indent()

def replaceString(s, mapping):
    for (key,val) in mapping.items():
        s = s.replace(key, val)
    return s

def replaceOutput(s):
    return replaceString(s, {
        u'–': '-',
        u'“': '',
        u'”': '',
        u'°': ' deg',
    })

def tell(s):
    s = replaceOutput(s) # This program requires ascii only.
    s = ' '*indentLevel*4 + s
    accumulator.append(s.rstrip())

def xmlquote(s):
    return replaceString(s, {
        '"': "&quot;",
        "&": "&amp;",
        "'": "&apos;",
        "<":  "&lt;",
        ">": "&gt;",
    })

def itemLine(item):
    itemType = item['variation']['type']
    if itemType != 'Group':
        if itemType == 'Element':
            itemType = 'Fixed'
        return '<item name="{}" type="{}">'.format(item['name'], itemType)
    else:
        return '<item name="{}">'.format(item['name'])

def render(s):
    root = json.loads(s)
    category = root['number']
    edition = root['edition']
    tell('<?xml version="1.0" encoding="UTF-8" ?>')
    tell('')
    tell('<!--')
    with indent:
        tell('Do not edit directly!')
        tell('This file is auto-generated from the original json specs file.')
        tell('sha1sum of the json input: {}'.format(hashlib.sha1(s).hexdigest()))
    tell('-->')
    tell('')
    tell('<category cat="{:03d}" edition="{}.{}">'.format(category, edition['major'], edition['minor']))
    with indent:
        tell('<dsc>Asterix Category {:03d}, edition {}.{}</dsc>'.format(category, edition['major'], edition['minor']))
        tell('<items>')
        with indent:
            [renderTopItem(item) for item in root['catalogue']]
        tell('</items>')
    with indent:
        renderUap(root['uap'])
    tell('</category>')
    return ''.join([line+'\n' for line in accumulator])

def renderTopItem(item):
    tell(itemLine(item))
    with indent:
        title = item['title']
        if title:
            tell('<dsc>{}</dsc>'.format(xmlquote(title)))
        renderVariation(item['variation'])
    tell('</item>')

def ffloat(val):
    val = format(float(val), '.16f')
    val = val.rstrip('0')
    if val[-1] == '.':
        val += '0'
    return val

def renderVariation(variation):

    def renderInteger(value):
        tell('<convert>')
        with indent:
            sig = '' if value['signed'] else 'unsigned '
            tell('<type>{}</type>'.format(sig + 'integer'))
            for i in value['constraints']:
                if i['type'] in ['>', '>=']:
                    tell('<min>{}</min>'.format(getNumber(i['value'])))
                if i['type'] in ['<', '<=']:
                    tell('<max>{}</max>'.format(getNumber(i['value'])))
        tell('</convert>')

    def renderQuantity(value):
        tell('<convert>')
        with indent:
            sig = '' if value['signed'] else 'unsigned '
            k = getNumber(value['scaling'])
            tell('<type>{}</type>'.format(sig + 'decimal'))

            fract = value['fractionalBits']
            if fract == 0:
                tell('<lsb>{}</lsb>'.format(ffloat(k)))
            else:
                tell('<lsb>{}/{}</lsb>'.format(ffloat(k), pow(2,fract)))

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
        def case1(val):
            rule = val['rule']
            t = rule['type']
            if t == 'Raw':
                pass
            elif t == 'Table':
                tell('<values>')
                with indent:
                    for key,value in rule['values']:
                        tell('<value val="{}" dsc="{}"/>'.format(key, xmlquote(value)))
                tell('</values>')
            elif t == 'String':
                f = case('string variatioin', rule['variation'],
                    ('StringAscii', lambda: tell('<convert><type>string</type></convert>')),
                    ('StringICAO', lambda: tell('<convert><type>ACID</type></convert>')),
                    ('StringOctal', lambda: None),
                    )
                f ()
            elif t == 'Integer':
                renderInteger(rule)
            elif t == 'Quantity':
                renderQuantity(rule)
            elif t == 'Bds':
                pass
            else:
                raise Exception('unexpected value type {}'.format(t))
        def case2(val):
            pass
        return renderRule(variation['content'], case1, case2)

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
                renderVariation(item['variation'])
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
        n1 = variation['first']
        n2 = variation['extents']
        tell('<len>({},{})</len>'.format(n1, n2))
        renderGroup()

    def renderRepetitive():
        var = variation['variation']
        if var['type'] == 'Element':
            # repetitive type expects additional level
            # so just make a 'Group' with a single item.
            renderVariation({
                "type": "Group",
                "items": [{
                    "definition": None,
                    "description": None,
                    "name": "item",
                    "remark": None,
                    "spare": False,
                    "title": "title",
                    "variation": var
                    }]
            })
        else:
            renderVariation(var)

    def renderExplicit():
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

def renderUap(uap):
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

