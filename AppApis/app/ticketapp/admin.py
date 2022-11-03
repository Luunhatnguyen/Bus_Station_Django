from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, F, ExpressionWrapper, FloatField, Q
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib.auth.models import Group
from .models import *
from django.utils.html import mark_safe
from datetime import datetime


class TicketAppAdminSite(admin.AdminSite):
    site_header = 'TICKET MANAGEMENT'

    def get_urls(self):
        return [
            path('stats-view/', self.stats_views),
            path('booking-view/', self.booking_view)
        ] + super().get_urls()

    def stats_views(self, request):

        routeStatic = Route.objects.all()

        month_route = request.GET.get('month_route', "")
        year_route = request.GET.get('year_route', "")
        filterRoute = request.GET.get('filterRoute', "")
        routePercent = 0

        if month_route and year_route and filterRoute:
            route = Route.objects.filter(id=filterRoute,
                this_busRoute_routeID__this_timeTable_busRouteID__date__month=month_route,
                this_busRoute_routeID__this_timeTable_busRouteID__date__year=year_route) \
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            r = Route.objects \
                .filter(this_busRoute_routeID__this_timeTable_busRouteID__date__month=month_route,
                        this_busRoute_routeID__this_timeTable_busRouteID__date__year=year_route) \
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            routeTotal = 0
            for i in r:
                routeTotal += i.timeTable
            routeStats = 0
            for i in route:
                routeStats += i.timeTable
            if routeTotal > 0:
                routePercent = routeStats / routeTotal * 100
            month_route = str.upper(datetime(1, int(month_route), 1).strftime("%B"))
        elif month_route and filterRoute:
            route = Route.objects.filter(id=filterRoute,
                this_busRoute_routeID__this_timeTable_busRouteID__date__month=month_route)\
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            r = Route.objects.filter(this_busRoute_routeID__this_timeTable_busRouteID__date__month=month_route,
                        this_busRoute_routeID__this_timeTable_busRouteID__date__year=datetime.now().year) \
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            routeTotal = 0
            for i in r:
                routeTotal += i.timeTable
            routeStats = 0
            for i in route:
                routeStats += i.timeTable
            if routeTotal > 0:
                routePercent = routeStats / routeTotal * 100
            month_route = str.upper(datetime(1, int(month_route), 1).strftime("%B"))
        elif year_route and filterRoute:
            route = Route.objects.filter(id=filterRoute,
                this_busRoute_routeID__this_timeTable_busRouteID__date__year=year_route) \
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            r = Route.objects \
                .filter(this_busRoute_routeID__this_timeTable_busRouteID__date__year=year_route) \
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            routeTotal = 0
            for i in r:
                routeTotal += i.timeTable
            routeStats = 0
            for i in route:
                routeStats += i.timeTable
            if routeTotal > 0:
                routePercent = routeStats / routeTotal * 100
        elif month_route and year_route:
            route = Route.objects.filter(this_busRoute_routeID__this_timeTable_busRouteID__date__month=month_route,
                this_busRoute_routeID__this_timeTable_busRouteID__date__year=year_route)\
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            month_route = str.upper(datetime(1, int(month_route), 1).strftime("%B"))
        elif filterRoute:
            route = Route.objects.filter(id=filterRoute)\
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            r = Route.objects.annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            routeTotal = 0
            for i in r:
                routeTotal += i.timeTable
            routeStats = 0
            for i in route:
                routeStats += i.timeTable
            if routeTotal > 0:
                routePercent = routeStats / routeTotal * 100
        elif month_route:
            route = Route.objects.filter(this_busRoute_routeID__this_timeTable_busRouteID__date__month=month_route) \
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            month_route = str.upper(datetime(1, int(month_route), 1).strftime("%B"))
        elif year_route:
            route = Route.objects.filter(this_busRoute_routeID__this_timeTable_busRouteID__date__year=year_route) \
                .annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
        else:
            route = Route.objects.annotate(timeTable=Count('this_busRoute_routeID__this_timeTable_busRouteID'))
            routeTotal = 0
            for i in route:
                routeTotal += i.timeTable
            routeStats = 0
            for i in route:
                routeStats += i.timeTable
            if routeTotal > 0:
                routePercent = routeStats / routeTotal * 100

        month_revenue = request.GET.get('month_revenue', "")
        year_revenue = request.GET.get('year_revenue', "")
        revenuePercent = 0

        if month_revenue and year_revenue:
            revenue = Route.objects \
                .filter(this_busRoute_routeID__this_timeTable_busRouteID__date__month=month_revenue,
                        this_busRoute_routeID__this_timeTable_busRouteID__date__year=year_revenue,
                        this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking__statusID=1) \
                .annotate(total=ExpressionWrapper(
                Count('this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking')
                * F('this_busRoute_routeID__price'),
                output_field=FloatField()))
            r = Route.objects \
                .filter(this_busRoute_routeID__this_timeTable_busRouteID__date__year=datetime.now().year,
                this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking__statusID=1) \
                .annotate(total=ExpressionWrapper(
                Count(
                    'this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking')
                * F('this_busRoute_routeID__price'),
                output_field=FloatField()))
            revenueTotal = 0
            for i in r:
                revenueTotal += i.total
            revenueStats = 0
            for i in revenue:
                revenueStats += i.total
            if revenueTotal > 0:
                revenuePercent = revenueStats / revenueTotal * 100
            month_revenue = str.upper(datetime(1, int(month_revenue), 1).strftime("%B"))
        elif month_revenue:
            revenue = Route.objects \
                .filter(this_busRoute_routeID__this_timeTable_busRouteID__date__month=month_revenue,
                        this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking__statusID=1) \
                .annotate(total=ExpressionWrapper(
                Count('this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking')
                * F('this_busRoute_routeID__price'),
                output_field=FloatField()))
            r = Route.objects \
                .filter(this_busRoute_routeID__this_timeTable_busRouteID__date__year=datetime.now().year,
                this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking__statusID=1) \
                .annotate(total=ExpressionWrapper(
                Count(
                    'this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking')
                * F('this_busRoute_routeID__price'),
                output_field=FloatField()))
            revenueTotal = 0
            for i in r:
                revenueTotal += i.total
            revenueStats = 0
            for i in revenue:
                revenueStats += i.total
            if revenueTotal > 0:
                revenuePercent = revenueStats / revenueTotal * 100
            month_revenue = str.upper(datetime(1, int(month_revenue), 1).strftime("%B"))
        elif year_revenue:
            revenue = Route.objects \
                .filter(this_busRoute_routeID__this_timeTable_busRouteID__date__year=year_revenue,
                        this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking__statusID=1) \
                .annotate(total=ExpressionWrapper(
                Count('this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking')
                * F('this_busRoute_routeID__price'),
                output_field=FloatField()))
            r = Route.objects \
                .filter(
                this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking__statusID=1) \
                .annotate(total=ExpressionWrapper(
                Count(
                    'this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking')
                * F('this_busRoute_routeID__price'),
                output_field=FloatField()))
            revenueTotal = 0
            for i in r:
                revenueTotal += i.total
            revenueStats = 0
            for i in revenue:
                revenueStats += i.total
            if revenueTotal > 0:
                revenuePercent = revenueStats / revenueTotal * 100
        else:
            revenue = Route.objects.filter(this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking__statusID=1)\
            .annotate(total=ExpressionWrapper(
            Count('this_busRoute_routeID__this_timeTable_busRouteID__this_booking_timeTable__this_bookinghistory_booking') * F('this_busRoute_routeID__price'),
            output_field=FloatField()))

        user = request.user

        return TemplateResponse(request, 'admin/stats-view.html', {
            'filterRoute': filterRoute,
            'routePercent': ("{0}%").format(float("{:.2f}".format(routePercent))),
            'routeStatic': routeStatic,
            'route': route,
            'month_route': month_route,
            'year_route': year_route,
            'year_range': range(1990, 2023),
            'revenue': revenue,
            'revenuePercent': ("{0}%").format(float("{:.2f}".format(revenuePercent))),
            'month_revenue': month_revenue,
            'year_revenue': year_revenue,
            'user': user
        })

    def booking_view(self, request):
        timeTable = TimeTable.objects.all()
        customer = User.objects.filter(is_staff=False)
        seat = Seat.objects.all()
        busRoute = BusRoute.objects.all()
        booking = Booking.objects.filter(this_bookinghistory_booking__statusID=2).order_by('-id')
        history = BookingHistory.objects.filter(active=1).exclude(statusID=1).order_by('-id')\
                .annotate(total=ExpressionWrapper(Count('bookingID__this_bookingDetail_booking')*F('bookingID__timeTable__busRouteID__price'),
                          output_field=FloatField()))
        detail = BookingDetail.objects.all()


        user = request.user

        return TemplateResponse(request, 'admin/booking-view.html', {
            'timeTable': timeTable,
            'customer': customer,
            'seat': seat,
            'busRoute': busRoute,
            'booking': booking,
            'history': history,
            'detail': detail,
            'user': user
        })


admin_site = TicketAppAdminSite('TICKET MANAGEMENT')
# Register your models here.


class GarageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address')
    list_display_links = list_display
    list_filter = ('name', 'created_date')
    search_fields = ('id', 'name')


class UserAdmin(admin.ModelAdmin):
    actions = ['set_password']
    list_display = ('id', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_display_links = list_display
    list_filter = ('is_staff', 'date_joined')
    search_fields = ('id', 'username', 'first_name', 'last_name')
    readonly_fields = ['image_view']

    def image_view(self, user):
        return mark_safe(
            "<img src='/static/{url}' alt='test' width='120' />".format(url=user.avatar.name)
        )

    def set_password(modeladmin, request, queryset):
        for q in queryset:
            usr = User.objects.get(id=q.id)
            if "pbkdf2_sha256$" not in usr.password:
                usr.set_password(usr.password)
                usr.save()


class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'city_from', 'to_garage')
    list_display_links = list_display
    search_fields = ('id', 'city_from', 'to_garage')


class TypeBusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = list_display
    search_fields = ('id', 'name')


class BusAdmin(admin.ModelAdmin):
    list_display = ('id', 'busModel', 'typeBusID')
    list_display_links = list_display
    list_filter = ('typeBusID', 'created_date')
    search_fields = ('id', 'busModel')


class BusRouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'busID', 'routeID', 'price')
    list_display_links = list_display
    list_filter = ('price', 'routeID', 'busID')
    search_fields = ('id', 'busID', 'routeID')


class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'location', 'typeBusID', 'active')
    list_display_links = list_display
    list_filter = ('location', 'typeBusID')
    search_fields = ('id', 'location', 'typeBusID')


class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'time', 'busRouteID', 'driver')
    list_display_links = list_display
    list_filter = ('time', 'driver')
    search_fields = ('id', 'date', 'time', 'busRouteID', 'driver')


class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customerID', 'name', 'phone', 'timeTable')
    list_display_links = list_display
    search_fields = ('id', 'customerID', 'name', 'phone', 'timeTable')


class BookingStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'statusValue')
    list_display_links = list_display
    search_fields = ('id', 'statusValue')


class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'bookingID', 'statusID', 'statusDate')
    list_display_links = list_display
    list_filter = ('statusID', 'statusDate')
    search_fields = ('id', 'bookingID', 'statusID', 'statusDate')


admin_site.register(User, UserAdmin)
admin_site.register(Garage, GarageAdmin)
admin_site.register(Route, RouteAdmin)
admin_site.register(TypeBus, TypeBusAdmin)
admin_site.register(Bus, BusAdmin)
admin_site.register(BusRoute, BusRouteAdmin)
admin_site.register(Seat, SeatAdmin)
admin_site.register(TimeTable, TimeTableAdmin)
admin_site.register(Booking, BookingAdmin)
admin_site.register(BookingStatus, BookingStatusAdmin)
admin_site.register(BookingHistory, BookingHistoryAdmin)
admin_site.register(Group)
admin_site.register(District)
admin_site.register(City)