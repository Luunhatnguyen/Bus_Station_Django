# Generated by Django 4.0.3 on 2023-03-31 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0002_route_destination_route_point'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='garageID',
        ),
        migrations.AddField(
            model_name='bus',
            name='garageID',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_garage', related_query_name='this_user_garage', to='ticketapp.garage'),
        ),
        migrations.DeleteModel(
            name='CodeConfirm',
        ),
    ]
