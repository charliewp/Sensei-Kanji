# Generated by Django 2.0.2 on 2019-08-09 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanji', '0018_auto_20190321_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='friendlyname',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
