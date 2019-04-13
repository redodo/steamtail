import urllib

from django import template

register = template.Library()


@register.simple_tag
def apps_done_count(queryset):
    return queryset.filter(unknown__isnull=False).count()


@register.filter
def similarity(diff):
    return (1 - diff / 2) * 100


@register.filter
def perc(value):
    return value * 100


@register.simple_tag(takes_context=True)
def toggle_param(context, param, value):
    parts = list(urllib.parse.urlparse(context.request.get_full_path()))
    query = set(urllib.parse.parse_qsl(parts[4]))
    part = (param, str(value))
    if part in query:
        query.remove(part)
    else:
        query.add(part)
    query = sorted(query, key=lambda i: int(i[1]))
    parts[4] = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(parts)


@register.simple_tag(takes_context=True)
def if_in_query(context, param, value, if_true, if_false=''):
    parts = list(urllib.parse.urlparse(context.request.get_full_path()))
    query = set(urllib.parse.parse_qsl(parts[4]))
    if (param, str(value)) in query:
        return if_true
    return if_false
