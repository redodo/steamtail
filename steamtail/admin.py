from django.contrib import admin

from .models import App


class AppInline(admin.TabularInline):
    model = App
    fields = ['id', 'name', 'type', 'modified_on']
    extra = 0
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj=obj)


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    search_fields = [
        'id',
        'name',
        'parent__name',
    ]
    autocomplete_fields = ['parent']
    list_per_page = 15
    list_display = [
        'id',
        'name',
        'type',
        'release_date',
        'modified_on',
    ]
    list_display_links = [
        'id',
        'name',
    ]
    list_filter = ['type']
    readonly_fields = [
        'id',
        'type',
        'name',
        'parent',
        'release_date',
        'tags',
        'info',
        'store_page_html',
        'store_page_retrieved_on',
    ]
    inlines = [AppInline]
    date_hierarchy = 'release_date'
