# Generated by Django 3.0.8 on 2020-08-15 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20200815_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(to='auctions.Listing'),
        ),
    ]
