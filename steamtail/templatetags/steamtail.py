from django import template

register = template.Library()


@register.simple_tag
def apps_done_count(queryset):
    return queryset.filter(unknown__isnull=False).count()


@register.filter
def similarity(diff):
    return (1 - diff / 2) * 100
