# Generated by Django 3.0.8 on 2020-08-14 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20200814_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='photo',
            field=models.URLField(blank=True, null=True),
        ),
    ]
