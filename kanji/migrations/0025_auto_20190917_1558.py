# Generated by Django 2.0.2 on 2019-09-17 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kanji', '0024_auto_20190917_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='description',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='kanji.Location'),
        ),
    ]
