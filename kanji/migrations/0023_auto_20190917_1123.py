# Generated by Django 2.0.2 on 2019-09-17 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kanji', '0022_auto_20190917_0848'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='username',
            new_name='slackuserid',
        ),
    ]
