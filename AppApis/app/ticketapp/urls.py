from rest_framework import routers
from django.urls import path, include
from . import views
from .admin import admin_site
from .views import *
from django.contrib.auth import views as auth_views

router = routers.DefaultRouter()
router.register(prefix='garages', viewset=views.GarageViewSet, basename='garage')
router.register(prefix='users', viewset=views.UserViewSet, basename='user')
router.register(prefix='routes', viewset=views.RouteViewSet, basename='route')
router.register(prefix='typebuss', viewset=views.TypeBusViewSet, basename='typebus')
router.register(prefix='buss', viewset=views.BusViewSet, basename='bus')
router.register(prefix='busroutes', viewset=views.BusRouteViewSet, basename='busroute')
router.register(prefix='busroute_post', viewset=views.BusRoutePostViewSet, basename='busroute_post')
router.register(prefix='seats', viewset=views.SeatViewSet, basename='seat')
router.register(prefix='timetables', viewset=views.TimeTableViewSet, basename='timetable')
router.register(prefix='bookings', viewset=views.BookingViewSet, basename='booking')
router.register(prefix='bookingstatuss', viewset=views.BookingStatusViewSet, basename='bookingstatus')
router.register(prefix='bookinghistorys', viewset=views.BookingHistoryViewSet, basename='bookinghistory')
router.register(prefix='city', viewset=views.CityViewSet, basename='city')
router.register(prefix='district', viewset=views.DistrictViewSet, basename='district')
router.register(prefix='bookingdetails', viewset=views.BookingDetailViewSet, basename='bookingdetail')
router.register(prefix='buscarrier', viewset=views.BusCarrierViewset, basename='buscarrier')
router.register(prefix='comments', viewset=views.CommentViewSet, basename='comment')
router.register(prefix='ratings', viewset=views.RatingViewSet, basename='rating')
router.register(prefix='momo', viewset=views.Momo, basename='momo')
<<<<<<< Updated upstream
router.register(prefix='send_mail_booking', viewset=views.BookingEmail, basename='send_mail_booking')

=======
router.register(prefix='SendSMS', viewset=views.SendSMS, basename='SendSMS')
>>>>>>> Stashed changes

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin_site.urls),
    path('send_mail/', views.SendMailAPIView.as_view(), name='send_mail'),
    path('oauth2-info/', views.OauthInfo.as_view()),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('social_auth/google/', views.GoogleSocialAuthView.as_view(), name="google_auth"),
    path('social_auth/facebook/', views.FacebookSocialAuthView.as_view(), name="facebook_auth"),
    path('reset-password/', include('django_rest_passwordreset.urls', namespace='reset-password')),
    path('admin-password-reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset',),
    path('admin-password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done',),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm',),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete',),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('carrier/', CarrierViewSet.as_view(), name='carierLogin'),
]