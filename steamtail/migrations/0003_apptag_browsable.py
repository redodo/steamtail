# Generated by Django 2.2 on 2019-04-03 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steamtail', '0002_auto_20190403_0649'),
    ]

    operations = [
        migrations.AddField(
            model_name='apptag',
            name='browsable',
            field=models.BooleanField(null=True, verbose_name='browsable'),
        ),
    ]
