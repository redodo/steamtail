# Generated by Django 2.2 on 2019-04-14 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steamtail', '0021_auto_20190414_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='total_reviews',
            field=models.PositiveIntegerField(null=True, verbose_name='total review count'),
        ),
    ]
