# Generated by Django 2.2 on 2019-04-03 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steamtail', '0003_apptag_browsable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apptag',
            name='browsable',
        ),
        migrations.AddField(
            model_name='apptag',
            name='browseable',
            field=models.BooleanField(null=True, verbose_name='browseable'),
        ),
    ]
