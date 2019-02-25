# Generated by Django 2.0.2 on 2019-02-25 01:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('idapplication', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='CoreType',
            fields=[
                ('idcoretype', models.BigAutoField(primary_key=True, serialize=False)),
                ('manufacturer', models.CharField(default='none', max_length=24)),
                ('model', models.CharField(default='none', max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('idcustomer', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='DeployState',
            fields=[
                ('iddeploystate', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('ideventlog', models.BigAutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='DateTime')),
                ('eventdata', models.CharField(max_length=24)),
                ('meshacktimemillis', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('ideventtype', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='Firmware',
            fields=[
                ('idfirmware', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('idlocation', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=24)),
                ('customer', models.ForeignKey(default=10000, on_delete=django.db.models.deletion.PROTECT, to='kanji.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('idnode', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=24)),
                ('coreid', models.CharField(max_length=24)),
                ('startofservicedate', models.DateField(blank=True, null=True)),
                ('endofservicedate', models.DateField(blank=True, null=True)),
                ('lastpingtimestamp', models.DateTimeField(null=True, verbose_name='DateTime')),
                ('pingintervalmillis', models.IntegerField(default=600000)),
                ('application', models.ForeignKey(default=10000, on_delete=django.db.models.deletion.PROTECT, to='kanji.Application')),
                ('coretype', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='kanji.CoreType')),
                ('customer', models.ForeignKey(default=10000, on_delete=django.db.models.deletion.PROTECT, to='kanji.Customer')),
                ('deploystate', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='kanji.DeployState')),
                ('firmware', models.ForeignKey(default=10000, on_delete=django.db.models.deletion.PROTECT, to='kanji.Firmware')),
            ],
        ),
        migrations.CreateModel(
            name='OnlineState',
            fields=[
                ('idonlinestate', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='PingLog',
            fields=[
                ('idpinglog', models.BigAutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='DateTime')),
                ('node', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='kanji.Node')),
                ('pingstate', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='kanji.OnlineState')),
            ],
        ),
        migrations.CreateModel(
            name='SensorType',
            fields=[
                ('idsensortype', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=32)),
                ('shorttag', models.CharField(default='none', max_length=32)),
                ('units', models.CharField(default='none', max_length=32)),
            ],
        ),
        migrations.AddField(
            model_name='node',
            name='lastpingstate',
            field=models.ForeignKey(default=10000, on_delete=django.db.models.deletion.PROTECT, to='kanji.OnlineState'),
        ),
        migrations.AddField(
            model_name='node',
            name='location',
            field=models.ForeignKey(default=10000, on_delete=django.db.models.deletion.PROTECT, to='kanji.Location'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='eventtype',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='kanji.EventType'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='node',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='kanji.Node'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='sensortype',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='kanji.SensorType'),
        ),
    ]
