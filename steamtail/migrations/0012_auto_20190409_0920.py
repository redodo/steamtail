# Generated by Django 2.2 on 2019-04-09 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steamtail', '0011_auto_20190409_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='friends_last_checked_on',
            field=models.DateTimeField(null=True, verbose_name='friends last checked on'),
        ),
    ]
