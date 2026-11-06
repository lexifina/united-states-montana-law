"""Montana HTML text, retaining the official publisher's punctuation."""
import html
import re


def add_unit(units, key, unit):
    n, candidate = 1, key
    while candidate in units:
        n += 1
        candidate = f'{key}-dup{n}'
    units[candidate] = unit
    return candidate


def write(path, corpus):
    import json
    import os
    with open(path + '.tmp', 'w', encoding='utf8', newline='\n') as f:
        f.write(json.dumps(corpus, ensure_ascii=False, indent=1) + '\n')
    os.replace(path + '.tmp', path)

_BLOCK = re.compile(r'<br\s*/?>|</?(?:p|div|li|ul|ol|tr|td|th|table|tbody|thead|h[1-6]|blockquote|dd|dt|dl)\b[^>]*>', re.I)
_TAG = re.compile(r'<[^>]+>')


def clean(s):
    s = html.unescape(_TAG.sub('', _BLOCK.sub(' ', s)))
    for c in '\u00a0\u2002\u2003\u2005\u2009\u202f':
        s = s.replace(c, ' ')
    s = s.replace('\ufeff', '').replace('\u00ad', '')
    return re.sub(r'[ \t\r\n]+', ' ', s).strip()


def blocks(node):
    """Yield text in document order, including text after nested lists and tables."""
    block_tags = {'p', 'div', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'thead', 'tbody', 'br', 'blockquote', 'dd', 'dt', 'dl'}
    lines, parts = [], []

    def flush():
        s = clean(''.join(parts))
        if s:
            lines.append(s)
        parts.clear()

    def walk(el):
        if el.text:
            # Text is already entity-decoded by the DOM. Escape it before clean's HTML decoding.
            parts.append(html.escape(el.text))
        for ch in el:
            if not isinstance(ch.tag, str):
                if ch.tail:
                    parts.append(html.escape(ch.tail))
                continue
            boundary = ch.tag.lower() in block_tags
            if boundary:
                flush()
            if ch.tag.lower() not in {'script', 'style', 'img'}:
                walk(ch)
            if boundary:
                flush()
            if ch.tail:
                parts.append(html.escape(ch.tail))

    walk(node)
    flush()
    return lines
