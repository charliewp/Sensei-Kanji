# Generated by Django 2.0.2 on 2019-09-19 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kanji', '0030_auto_20190918_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='node',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='kanji.Node'),
        ),
    ]
