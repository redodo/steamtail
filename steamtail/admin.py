from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import App, Tag, User
from .tasks import update_app, update_user_apps


class AppInline(admin.TabularInline):
    model = App
    fields = ['id', 'name', 'type', 'modified_on']
    extra = 0
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj=obj)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
    ]
    list_display = [
        'id',
        'name',
    ]
    list_display_links = [
        'id',
        'name',
    ]
    readonly_fields = [
        'id',
        'name',
    ]


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    change_list_template = 'steamtail/admin/app_change_list.html'
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
        'unknown',
        'release_date',
        'modified_on',
    ]
    list_display_links = [
        'id',
        'name',
    ]
    list_filter = [
        'type',
        'unknown',
        'is_free',
        'coming_soon',
        'tags',
    ]
    readonly_fields = [
        'id',
        'type',
        'name',
        'unknown',
        'parent',
        'review_score',
        'total_reviews',
        'positive_reviews',
        'negative_reviews',
        'coming_soon',
        'release_date',
        'release_date_text',
        'tags',
        'tag_votes',
        'short_description',
        'is_free',
    ]
    inlines = [AppInline]
    date_hierarchy = 'release_date'
    actions = [
        'update_apps',
        'update_pending_apps',
    ]

    def update_apps(self, request, queryset):
        for app in queryset:
            update_app(app)
    update_apps.short_description = _(
        'Update selected apps'
    )

    def update_pending_apps(self, request, queryset):
        for app in queryset.filter(unknown=None):
            update_app(app)
    update_pending_apps.short_description = _(
        'Update pending selected apps'
    )


class UserAppOwnershipInline(admin.TabularInline):
    model = User.apps.through
    fields = ['app', 'hours_played']
    readonly_fields = ['app', 'hours_played']
    extra = 0
    max_num = 0
    can_delete = False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['id']
    autocomplete_fields = ['friends', 'apps']
    list_display = [
        'id',
        'is_public',
        'is_ownership_public',
        'is_playtime_public',
        'friends_last_checked_on',
        'apps_last_checked_on',
    ]
    list_per_page = 15
    list_filter = [
        'is_public',
        'is_ownership_public',
        'is_playtime_public',
    ]
    inlines = [
        UserAppOwnershipInline,
    ]
    readonly_fields = [
        'id',
        'friends',
        'is_public',
        'is_ownership_public',
        'is_playtime_public',
        'friends_last_checked_on',
        'apps_last_checked_on',
    ]
    actions = [
        'update_user_apps',
    ]

    def update_user_apps(self, request, queryset):
        for user in queryset:
            update_user_apps(user.id)
    update_user_apps.short_description = _(
        'Force update user apps'
    )
