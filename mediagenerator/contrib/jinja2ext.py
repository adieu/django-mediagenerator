from jinja2 import nodes, TemplateAssertionError, Markup as mark_safe
from jinja2.ext import Extension
from mediagenerator.generators.bundles.utils import _render_include_media

class MediaExtension(Extension):
    tags = set(['include_media'])

    def __init__(self, environment):
        self.environment = environment

    def parse(self, parser):
        token = parser.stream.next()
        args = [parser.parse_expression()]
        kwargs = []
        while parser.stream.current.type != 'block_end':
            if kwargs:
                parser.stream.expect('comma')

            if parser.stream.skip_if('colon'):
                break

            name = parser.stream.expect('name')
            if name.value in kwargs:
                parser.fail('variable %r defined twice.' %
                            name.value, name.lineno,
                            exc=TemplateAssertionError)
            parser.stream.expect('assign')
            key = name.value
            value = parser.parse_expression()
            kwargs.append(nodes.Keyword(key, value,
                                        lineno=value.lineno))
        return nodes.Output([self.call_method('_render', args, kwargs)]).set_lineno(token.lineno)

    def _render(self, bundle, **variation):
        return mark_safe(_render_include_media(bundle, variation))
