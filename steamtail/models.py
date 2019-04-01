from django.db import models
from django.utils.translation import gettext_lazy as _


class App(models.Model):
    id = models.BigIntegerField(
        _('app ID'),
        primary_key=True,
        editable=False,
    )
    type = models.CharField(
        _('app type'),
        max_length=32,
        blank=True,
        null=True,
    )
    name = models.TextField(
        _('app name'),
    )
    info = models.BinaryField(
        _('raw app info'),
        blank=True,
        null=True,
    )
    created_on = models.DateTimeField(
        _('created on'),
        auto_now_add=True,
    )
    modified_on = models.DateTimeField(
        _('modified on'),
        auto_now=True,
    )
    parent = models.ForeignKey(
        'App',
        verbose_name=_('parent app'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    release_date = models.DateField(
        _('release date'),
        blank=True,
        null=True,
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='apps',
        verbose_name=_('tags'),
    )
    store_page_html = models.BinaryField(
        _('store page html'),
        blank=True,
        null=True,
    )
    store_page_retrieved_on = models.DateTimeField(
        _('store page retrieved on'),
        blank=True,
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
        _('ID'),
        primary_key=True,
        editable=False,
    )
    name = models.CharField(
        _('tag name'),
        max_length=255,
    )

    class Meta:
        ordering = ['id', 'name']
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return 'https://store.steampowered.com/tags/en/{}/'.format(self.name)
