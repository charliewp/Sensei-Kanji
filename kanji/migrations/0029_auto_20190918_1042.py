# Generated by Django 2.0.2 on 2019-09-18 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kanji', '0028_auto_20190918_1040'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='idissue',
            new_name='idticket',
        ),
        migrations.RenameField(
            model_name='ticketstatus',
            old_name='idissuestatus',
            new_name='idticketstatus',
        ),
    ]
