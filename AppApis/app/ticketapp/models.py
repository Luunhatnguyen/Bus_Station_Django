from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken


class ModelBase(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class City(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class District(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    cityID = models.ForeignKey(City,
                               related_name='district_city',
                               related_query_name='this_district_city',
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Garage(ModelBase):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, unique=True)
    cityID = models.ForeignKey(City,
                                related_name='garage_city',
                                related_query_name='this_garage_city',
                                on_delete=models.CASCADE)
    districtID = models.ForeignKey(District,
                                related_name='garage_district',
                                related_query_name='this_garage_district',
                                on_delete=models.CASCADE)

    def __str__(self):
        return self.name


AUTH_PROVIDERS = {'facebook': 'facebook',
                  'google': 'google',
                  'default': 'default'
              }


class User(AbstractUser):
    last_login = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(null=True, upload_to='users/%Y/%m')
    phone = models.CharField(max_length=11, unique=True, null=True)
    email = models.EmailField(unique=True, null=True)
    isCarrier = models.BooleanField(default=False)

    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('default'))

    def __str__(self):
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class Route(ModelBase):
    image = models.ImageField(null=True, upload_to='image/%Y/%m')
    distance = models.CharField(max_length=255, default="0")
    point  = models.CharField(max_length=255, default="0")
    destination = models.CharField(max_length=255, default="0")
    hours = models.CharField(max_length=255, default="0")
    city_from = models.ForeignKey(City,
                               related_name='route_city',
                               related_query_name='this_route_city',
                               on_delete=models.CASCADE)
    to_garage = models.ForeignKey(Garage,
                                related_name='route_to_garage',
                                related_query_name='this_route_to_garage',
                                on_delete=models.CASCADE)
    rating = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('city_from', 'to_garage')

    def __str__(self):
        return ("{0}_{1}").format(self.city_from, self.to_garage)


class TypeBus(ModelBase):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# Tạo table cho phí hệ thống dành cho nhà xe
class HireOption(ModelBase):
    id = models.CharField(primary_key=True, max_length=255)
    option = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    fee = models.FloatField()
    numberOfVehicles = models.IntegerField(default=1)
    rentalPeriod = models.IntegerField(default=1)


class Carrier(ModelBase):
    userID = models.ForeignKey(User,
                               related_name='carrier',
                               related_query_name='this_carrier_user',
                               null=True,
                               on_delete=models.CASCADE)
    nameCarrier = models.CharField(max_length=255, unique=True)
    garageID = models.ForeignKey(Garage,
                                 related_name='carrier_garage',
                                 related_query_name='this_carrier_garage',
                                 null=True,
                                 on_delete=models.SET_NULL, blank=True)
    optionID = models.ForeignKey(HireOption,
                                 related_name='carrier',
                                 related_query_name='this_carrier_optionID',
                                 null=True,
                                 on_delete=models.CASCADE)
    class StatusCode(models.TextChoices):
        APPROVE = 'APPROVE'
        NOTAPPROVE = 'NOT APPROVE'
        PENDING = 'PENDING'

    status_code = models.CharField(
        max_length=12,
        choices=StatusCode.choices,
        default=StatusCode.PENDING,
    )

class Bus(ModelBase):
    typeBusID = models.ForeignKey(TypeBus,
                                related_name='bus_typeBus',
                                related_query_name='this_bus_typeBus',
                                on_delete=models.CASCADE)
    carrierID = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    numberplate = models.CharField(max_length=255, unique=True,default=0)
    image = models.ImageField(null=True, upload_to='image/%Y/%m')
    description = models.CharField(max_length=255, default="0")
    rating = models.FloatField(null=True, blank=True)
    garageID = models.ForeignKey(Garage,
                                 related_name='user_garage',
                                 related_query_name='this_user_garage',
                                 null=True,
                                 on_delete=models.SET_NULL, blank=True)

    def __str__(self):
        return self.name


class BusRoute(ModelBase):
    busID = models.ForeignKey(Bus,
                                related_name='busRoute_busID',
                                related_query_name='this_busRoute_busID',
                                on_delete=models.CASCADE)
    routeID = models.ForeignKey(Route,
                                related_name='busRoute_routeID',
                                related_query_name='this_busRoute_routeID',
                                on_delete=models.CASCADE)
    price = models.FloatField()

    class Meta:
        unique_together = ('busID', 'routeID')

    def __str__(self):
        return ("{0}_{1}").format(self.busID, self.routeID)


class Seat(ModelBase):
    location = models.CharField(max_length=255)
    typeBusID = models.ForeignKey(TypeBus,
                                related_name='seat_typeBus',
                                related_query_name='this_seat_typeBus',
                                on_delete=models.CASCADE)

    def __str__(self):
        return ("{0}_{1}").format(self.location, self.typeBusID)


class TimeTable(ModelBase):
    date = models.DateField()
    time = models.TimeField()
    driver = models.ForeignKey(User,
                               related_name='timeTable_user',
                               related_query_name='this_timeTable_user',
                               null=True,
                               on_delete=models.SET_NULL)
    busRouteID = models.ForeignKey(BusRoute,
                                related_name='timeTable_busRouteID',
                                related_query_name='this_timeTable_busRouteID',
                                on_delete=models.CASCADE)

    def __str__(self):
        return ("{0}_{1}_{2}").format(self.date, self.time, self.busRouteID)


class Booking(ModelBase):
    customerID = models.ForeignKey(User,
                                related_name='booking_user',
                                related_query_name='this_booking_user',
                                null=True,blank=True,
                                on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255)
    timeTable = models.ForeignKey(TimeTable,
                                  related_name='booking_timeTable',
                                  related_query_name='this_booking_timeTable',
                                  null=True,
                                  on_delete=models.SET_NULL)
    send_mail = models.BooleanField(default=False)

    def __str__(self):
        return ("{0}_{1}_{2}_{3}").format(self.id, self.customerID, self.name, self.phone)


class BookingDetail(ModelBase):
    bookingID = models.ForeignKey(Booking,
                                  related_name='bookingDetail_booking',
                                  related_query_name='this_bookingDetail_booking',
                                  on_delete=models.CASCADE)
    from_garage = models.ForeignKey(Garage,
                                related_name='booking_from_garage',
                                related_query_name='this_booking_from_garage',
                                null=True,
                                on_delete=models.SET_NULL)
    seatID = models.ForeignKey(Seat,
                                related_name='booking_seat',
                                related_query_name='this_booking_seat',
                                null=True,
                                on_delete=models.SET_NULL)


class BookingStatus(ModelBase):
    statusValue = models.CharField(max_length=255)

    def __str__(self):
        return self.statusValue


class BookingHistory(ModelBase):
    bookingID = models.OneToOneField(Booking,
                                     related_query_name='this_bookinghistory_booking',
                                     on_delete=models.CASCADE)
    statusID = models.ForeignKey(BookingStatus,
                                related_name='bookinghistory_status',
                                related_query_name='this_bookinghistory_status',
                                null=True,
                                on_delete=models.SET_NULL)
    statusDate = models.DateTimeField(auto_now_add=True)


class Comment(ModelBase):
    content = models.TextField()
    busroute = models.ForeignKey(BusRoute,
                               related_name='comments',
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class ActionBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    busroute = models.ForeignKey(BusRoute, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Rating(ActionBase):
    rate = models.SmallIntegerField(default=0)
    comment = models.ForeignKey(Comment,
                                related_name='rating_comment',
                                related_query_name='this_rating_comment',
                                null=True,
                                on_delete=models.CASCADE)

