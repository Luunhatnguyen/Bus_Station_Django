# Generated by Django 4.0.3 on 2023-03-12 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='destination',
            field=models.CharField(default='0', max_length=255),
        ),
        migrations.AddField(
            model_name='route',
            name='point',
            field=models.CharField(default='0', max_length=255),
        ),
    ]
