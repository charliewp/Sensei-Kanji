# Generated by Django 2.0.2 on 2019-03-21 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanji', '0015_location_imageurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='gridlocator',
            field=models.CharField(max_length=8, null=True),
        ),
    ]
