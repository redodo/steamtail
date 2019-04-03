from django import template

register = template.Library()


@register.simple_tag
def apps_done_count(queryset):
    return queryset.filter(unknown__isnull=False).count()
