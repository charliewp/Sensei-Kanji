# Generated by Django 2.0.2 on 2019-09-18 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kanji', '0026_auto_20190917_1617'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Issue',
            new_name='Ticket',
        ),
    ]
