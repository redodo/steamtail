# Generated by Django 2.2 on 2019-04-13 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steamtail', '0017_auto_20190413_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='tag_votes',
            field=models.PositiveIntegerField(null=True, verbose_name='total number of votes on tags'),
        ),
    ]