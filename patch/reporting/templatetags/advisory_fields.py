import textwrap

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
@stringfilter
def advisory_source(value):
    return dict(settings.ADVISORY_SOURCES)[value]

@register.filter
@stringfilter
def advisory_release(value):
    return dict(settings.RELEASES)[value]

@register.filter
@stringfilter
def advisory_severity(value):
    if value == '0':
        return ''

    return dict(settings.ADVISORY_SEVERITIES)[int(value)]

@register.filter
@stringfilter
def ignore_none(value):
    if value == 'None':
        return ''

    return value

@register.filter(needs_autoescape=True)
@stringfilter
def paragraphbreaks(value, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    value = textwrap.dedent(value).replace('\r\n', '\n') # fix windows linebreaks

    result = '<p>%s</p>' % '</p><p>'.join(esc(value).split('\n\n'))
    return mark_safe(result)

