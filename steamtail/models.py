from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _


class App(models.Model):
    id = models.BigIntegerField(
        _('app ID'),
        primary_key=True,
        editable=False,
    )
    created_on = models.DateTimeField(
        _('created on'),
        auto_now_add=True,
    )
    modified_on = models.DateTimeField(
        _('modified on'),
        auto_now=True,
    )
    type = models.CharField(
        _('app type'),
        max_length=32,
        null=True,
    )
    name = models.TextField(
        _('app name'),
    )
    short_description = models.TextField(
        _('short description'),
        null=True,
    )
    parent = models.ForeignKey(
        'App',
        verbose_name=_('parent app'),
        on_delete=models.SET_NULL,
        null=True,
    )
    is_free = models.BooleanField(
        _('is free'),
        null=True,
    )
    coming_soon = models.BooleanField(
        _('coming soon'),
        null=True,
    )
    release_date = models.DateField(
        _('release date'),
        null=True,
    )
    tags = models.ManyToManyField(
        'Tag',
        through='AppTag',
        related_name='apps',
        verbose_name=_('tags'),
    )

    unknown = models.BooleanField(
        _('unknown'),
        null=True,  # default is unknown
    )

    # Raw unprocessed data gathered from Steam.
    raw_info = JSONField(
        _('raw app info'),
        null=True,
    )
    raw_store_page = models.BinaryField(
        _('raw store page'),
        null=True,
    )

    class Meta:
        ordering = ['id', 'name']
        verbose_name = _('app')
        verbose_name_plural = _('apps')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return 'https://store.steampowered.com/app/{}/'.format(self.id)


class Tag(models.Model):
    id = models.BigIntegerField(
        _('tag ID'),
        primary_key=True,
        editable=False,
    )
    name = models.CharField(
        _('tag name'),
        max_length=255,
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return 'https://store.steampowered.com/tags/en/{}/'.format(self.name)


class AppTag(models.Model):
    """Records a tag to an app with number of votes"""
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )
    votes = models.PositiveIntegerField(
        _('votes'),
    )
    browseable = models.BooleanField(
        _('browseable'),
        null=True,
    )

    class Meta:
        unique_together = ('app', 'tag')


class User(models.Model):
    id = models.BigIntegerField(
        _('steam64 id'),
        primary_key=True,
        editable=False,
    )
    apps = models.ManyToManyField(
        App,
        through='UserApp',
        related_name='users',
        verbose_name=_('apps'),
    )
    friends = models.ManyToManyField(
        'User',
        verbose_name=_('friends'),
    )
    last_visited_on = models.DateTimeField(
        _('last visited on'),
        null=True,
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return 'https://steamcommunity.com/profiles/{}'.format(self.id)


class UserApp(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
    )
    hours_played = models.DecimalField(
        _('hours played'),
        max_digits=10,
        decimal_places=2,
        null=True,
    )
    last_played = models.DateTimeField(
        _('last played'),
        null=True,
    )

    class Meta:
        unique_together = ('user', 'app')
