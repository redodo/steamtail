import re

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
    release_date_text = models.CharField(
        _('release date text'),
        max_length=255,
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

    tag_votes = models.PositiveIntegerField(
        _('total number of votes on tags'),
        null=True,
    )

    total_reviews = models.PositiveIntegerField(
        _('total review count'),
        null=True,
    )
    positive_reviews = models.PositiveIntegerField(
        _('positive review count'),
        null=True,
    )
    negative_reviews = models.PositiveIntegerField(
        _('negative review count'),
        null=True,
    )
    review_score = models.FloatField(
        _('review score'),
        null=True,
    )

    def save(self, *args, **kwargs):
        if self.positive_reviews or self.negative_reviews:
            self.total_reviews = self.positive_reviews + self.negative_reviews
            self.review_score = self.positive_reviews / self.total_reviews
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['id', 'name']
        verbose_name = _('app')
        verbose_name_plural = _('apps')

    def __str__(self):
        return self.name

    def cleaned_name(self):
        return re.sub('[®©™]', '', self.name)

    def get_absolute_url(self):
        return 'https://store.steampowered.com/app/{}/'.format(self.id)

    def get_image_url(self):
        return 'https://steamcdn-a.akamaihd.net/steam/apps/{}/header.jpg'.format(self.id)

    def get_large_image_url(self):
        return 'https://steamcdn-a.akamaihd.net/steam/apps/{}/capsule_616x353.jpg'.format(self.id)

    def get_small_image_url(self):
        return 'https://steamcdn-a.akamaihd.net/steam/apps/{}/header_292x136.jpg'.format(self.id)

    def get_background_image_url(self):
        return 'https://steamcdn-a.akamaihd.net/steam/apps/{}/page_bg_generated_v6b.jpg'.format(self.id)


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
    share = models.FloatField(
        _('share of votes'),
        null=True,
    )
    browseable = models.BooleanField(
        _('browseable'),
        null=True,
    )

    class Meta:
        ordering = ['-votes']
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
        'self',
        verbose_name=_('friends'),
    )
    friends_last_checked_on = models.DateTimeField(
        _('friends last checked on'),
        null=True,
    )
    apps_last_checked_on = models.DateTimeField(
        _('apps last checked on'),
        null=True,
    )
    is_public = models.BooleanField(
        _('is profile public'),
        null=True,
    )
    is_ownership_public = models.BooleanField(
        _('is ownership public'),
        null=True,
    )
    is_playtime_public = models.BooleanField(
        _('is playtime public'),
        null=True,
    )

    class Meta:
        ordering = ['id']
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return str(self.id)

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

    class Meta:
        unique_together = ('user', 'app')
