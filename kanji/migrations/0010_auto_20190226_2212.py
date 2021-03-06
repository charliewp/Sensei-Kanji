# Generated by Django 2.0.2 on 2019-02-27 03:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kanji', '0009_channel_sensor'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeshNetwork',
            fields=[
                ('idmeshnetwork', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=24)),
                ('password', models.CharField(max_length=24)),
            ],
        ),
        migrations.AddField(
            model_name='node',
            name='channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='kanji.Channel'),
        ),
        migrations.AddField(
            model_name='node',
            name='meshnetwork',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='kanji.MeshNetwork'),
        ),
    ]
