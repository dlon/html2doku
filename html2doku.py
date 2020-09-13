#!/usr/bin/python

import argparse
from html.parser import HTMLParser
import sys


class GenericTagHandler:
    def __init__(self, tag, attrs):
        self.tag = tag
        if attrs:
            attrs = ' '.join('{}="{}"'.format(attr, value) for attr, value in attrs)
            self.content = ['<{} {}>'.format(tag, attrs)]
        else:
            self.content = ['<{}>'.format(tag, attrs)]

    def handle_data(self, data):
        self.content.append(data)

    def end(self):
        self.content.append('</{}>'.format(self.tag))
        return ''.join(self.content)

class ATagHandler:
    def __init__(self, tag, attrs):
        if len(attrs) > 1:
            raise Exception('contains unknown attributes')
        self.href = dict(attrs)['href']
        self.content = []

    def handle_data(self, data):
        self.content.append(data)

    def end(self):
        return '[[{}|{}]]'.format(self.href, ''.join(self.content))

class FormatTagHandler:
    def __init__(self, tag, attrs):
        if tag in ('b', 'strong'):
            self.code = '**'
        elif tag in ('i', 'em'):
            self.code = '//'
        self.content = []

    def handle_data(self, data):
        self.content.append(data)

    def end(self):
        return '{}{}{}'.format(self.code, ''.join(self.content), self.code)

class SpanTagHandler:
    def __init__(self, tag, attrs):
        attrs = dict(attrs)
        style_attr = attrs['style']
        style_attr = dict((a.strip(), b.strip()) for a,b in (attr.split(':') for attr in attrs['style'].split(';') if attr))

        if len(style_attr) != 1:
            raise Exception('unknown attributes')
        if style_attr.get('text-decoration') != 'line-through':
            raise Exception('only line-through is supported for span elements')

        self.content = []

    def handle_data(self, data):
        self.content.append(data)

    def end(self):
        return '<del>{}</del>'.format(''.join(self.content))

class HeaderTagHandler:
    def __init__(self, tag, attrs):
        level = max(1, 8 - int(tag[1]))
        self.wrap = '=' * level
        self.content = []

    def handle_data(self, data):
        self.content.append(data)

    def end(self):
        return '\n{} {} {}\n'.format(self.wrap, ''.join(self.content), self.wrap)

class ListItemHandler:
    def __init__(self, tag, attrs):
        self.content = []

    def handle_data(self, data):
        self.content.append(data)

    def end(self):
        return self

class ListHandler:
    def __init__(self, tag, attrs):
        if tag == 'ul':
            self.ordered = False
        elif tag == 'ol':
            self.ordered = True
        self.items = []

    def handle_data(self, data):
        if isinstance(data, ListItemHandler):
            self.items.append(''.join(data.content))
        else:
            # TODO: handle whitespace, etc.
            pass

    def end(self):
        if self.ordered:
            prefix = '-'
        else:
            prefix = '*'

        data = []
        for item in self.items:
            data.append('  {} {}'.format(prefix, item))

        return '\n'.join(data)

class BreakHandler:
    def __init__(self, tag, attrs):
        pass

    def handle_data(self, data):
        raise Exception('unexpected content in <br> element')

    def end(self):
        return '\\\\ '

tag_handlers = {
    'a': ATagHandler,
    'em': FormatTagHandler,
    'i': FormatTagHandler,
    'strong': FormatTagHandler,
    'b': FormatTagHandler,
    'span': SpanTagHandler,
    'h1': HeaderTagHandler,
    'h2': HeaderTagHandler,
    'h3': HeaderTagHandler,
    'h4': HeaderTagHandler,
    'h5': HeaderTagHandler,
    'ul': ListHandler,
    'ol': ListHandler,
    'li': ListItemHandler,
    'br': BreakHandler,
}
self_closing_tags = ('br',)

class Html2DokuParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.handlers = []
        self.handler = None

        self.output = []

    def handle_starttag(self, tag, attrs):
        handler = tag_handlers.get(tag)
        if handler:
            try:
                self.handlers.append(handler(tag, attrs))
            except Exception as e:
                print('warning: using generic tag handler for tag:', tag, attrs, file=sys.stderr)
                print('    caused by exception: {}: {}'.format(type(e).__name__, e), file=sys.stderr)
                self.handlers.append(GenericTagHandler(tag, attrs))
        else:
            print('warning: using generic tag handler for tag:', tag, attrs, file=sys.stderr)
            self.handlers.append(GenericTagHandler(tag, attrs))

        if tag in self_closing_tags:
            self.handle_endtag('')

    def handle_endtag(self, tag):
        if tag in self_closing_tags:
            return

        handler = self.handlers.pop()
        data = handler.end()
        self.handle_data(data)

    def handle_data(self, data):
        if self.handlers:
            self.handlers[-1].handle_data(data)
        else:
            self.output.append(data)

def main():
    argparser = argparse.ArgumentParser(description='Convert HTML to DokuWiki markup')
    argparser.add_argument('--input', '-i', type=argparse.FileType('r'), default=sys.stdin, help='an HTML document (stdin if not specified)')
    argparser.add_argument('--output', '-o', type=argparse.FileType('w'), default=sys.stdout, help='destination file for the DokuWiki markup (stdout if not specified)')
    args = argparser.parse_args()

    parser = Html2DokuParser()

    parser.feed(args.input.read())
    data = ''.join(parser.output)
    args.output.write(data)

if __name__ == '__main__':
    main()

