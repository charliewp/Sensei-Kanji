# Generated by Django 2.0.2 on 2019-03-21 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanji', '0014_node_setupstring'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='imageurl',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
