# Generated by Django 2.2 on 2019-04-03 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('steamtail', '0004_auto_20190403_0846'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['name'], 'verbose_name': 'tag', 'verbose_name_plural': 'tags'},
        ),
    ]
