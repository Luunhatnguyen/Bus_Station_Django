# Generated by Django 4.0.3 on 2023-03-31 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0003_remove_user_garageid_bus_garageid_delete_codeconfirm'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='numberplate',
            field=models.CharField(default=0, max_length=255, unique=True),
        ),
    ]
