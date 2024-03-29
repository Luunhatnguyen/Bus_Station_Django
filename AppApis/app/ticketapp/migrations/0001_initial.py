# Generated by Django 4.0.3 on 2023-03-11 10:32

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now_add=True)),
                ('avatar', models.ImageField(null=True, upload_to='users/%Y/%m')),
                ('phone', models.CharField(max_length=11, null=True, unique=True)),
                ('email', models.EmailField(max_length=254, null=True, unique=True)),
                ('isCarrier', models.BooleanField(default=False)),
                ('auth_provider', models.CharField(default='default', max_length=255)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('send_mail', models.BooleanField(default=False)),
                ('customerID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_user', related_query_name='this_booking_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BookingStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('statusValue', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Bus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('busModel', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('image', models.ImageField(null=True, upload_to='image/%Y/%m')),
                ('description', models.CharField(default='0', max_length=255)),
                ('rating', models.FloatField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BusRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('price', models.FloatField()),
                ('busID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='busRoute_busID', related_query_name='this_busRoute_busID', to='ticketapp.bus')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('busroute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='ticketapp.busroute')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('cityID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='district_city', related_query_name='this_district_city', to='ticketapp.city')),
            ],
        ),
        migrations.CreateModel(
            name='Garage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('address', models.CharField(max_length=255, unique=True)),
                ('cityID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='garage_city', related_query_name='this_garage_city', to='ticketapp.city')),
                ('districtID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='garage_district', related_query_name='this_garage_district', to='ticketapp.district')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TypeBus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CodeConfirm',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('code', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TimeTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('busRouteID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeTable_busRouteID', related_query_name='this_timeTable_busRouteID', to='ticketapp.busroute')),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeTable_user', related_query_name='this_timeTable_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(max_length=255)),
                ('typeBusID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seat_typeBus', related_query_name='this_seat_typeBus', to='ticketapp.typebus')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(null=True, upload_to='image/%Y/%m')),
                ('distance', models.CharField(default='0', max_length=255)),
                ('hours', models.CharField(default='0', max_length=255)),
                ('rating', models.FloatField(blank=True, null=True)),
                ('city_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_city', related_query_name='this_route_city', to='ticketapp.city')),
                ('to_garage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_to_garage', related_query_name='this_route_to_garage', to='ticketapp.garage')),
            ],
            options={
                'unique_together': {('city_from', 'to_garage')},
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('rate', models.SmallIntegerField(default=0)),
                ('busroute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticketapp.busroute')),
                ('comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rating_comment', related_query_name='this_rating_comment', to='ticketapp.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='busroute',
            name='routeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='busRoute_routeID', related_query_name='this_busRoute_routeID', to='ticketapp.route'),
        ),
        migrations.AddField(
            model_name='bus',
            name='typeBusID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bus_typeBus', related_query_name='this_bus_typeBus', to='ticketapp.typebus'),
        ),
        migrations.AddField(
            model_name='bus',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BookingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('statusDate', models.DateTimeField(auto_now_add=True)),
                ('bookingID', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_query_name='this_bookinghistory_booking', to='ticketapp.booking')),
                ('statusID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bookinghistory_status', related_query_name='this_bookinghistory_status', to='ticketapp.bookingstatus')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BookingDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('bookingID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookingDetail_booking', related_query_name='this_bookingDetail_booking', to='ticketapp.booking')),
                ('from_garage', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_from_garage', related_query_name='this_booking_from_garage', to='ticketapp.garage')),
                ('seatID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_seat', related_query_name='this_booking_seat', to='ticketapp.seat')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='timeTable',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_timeTable', related_query_name='this_booking_timeTable', to='ticketapp.timetable'),
        ),
        migrations.AddField(
            model_name='user',
            name='garageID',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_garage', related_query_name='this_user_garage', to='ticketapp.garage'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='busroute',
            unique_together={('busID', 'routeID')},
        ),
    ]
