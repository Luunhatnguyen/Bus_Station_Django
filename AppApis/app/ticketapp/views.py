from django.conf import settings
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, status, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from .perms import CommentOwnerPerms, RatingOwnerPerms
from .paginators import *
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
import datetime
import json
import urllib.request
import urllib
import uuid
import requests
import hmac
import hashlib


class GarageViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = Garage.objects.filter(active=True)
    serializer_class = GarageSerializer


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]

    def get_permissions(self):
        if self.action == 'get_current_user':
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path="current-user")
    def get_current_user(self, request):
        return Response(self.serializer_class(request.user, context={'request': request}).data, status=status.HTTP_200_OK)

    # API thay đổi mật khẩu
    @action(methods=['post'], detail=False, url_path="change-password")
    def change_password(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        account = request.user

        if old_password is not None and new_password is not None and old_password != new_password:
            if not account.check_password(old_password):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            account.set_password(new_password)
            account.save()
            response = {
                'status': 'success',
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response({"Message": ["Errors."]}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView:
    @receiver(reset_password_token_created)
    def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
        link_reset = "http://localhost:3000/reset-password/{}".format(reset_password_token.key)
        home = "http://localhost:3000"
        subject = "Link Reset Password for {title}".format(title="Website Trip")
        from_email = '1951052134nguyen@ou.edu.vn'
        to = reset_password_token.user.email

        html_content = render_to_string('email_reset_pass.html', {'title': subject, 'link': link_reset, 'home': home})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class OauthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)


class RouteViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = Route.objects.filter(active=True)
    serializer_class = RouteSerializer
    pagination_class = TripPagination

    def get_queryset(self):
        list_bus = Route.objects.filter(active=True)

        # lọc theo rate
        rate = self.request.query_params.get('rate')
        if rate is not None:
            list_bus = list_bus.filter(rating=rate)

        return list_bus


class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            user = serializer.save()

            return JsonResponse({
                'message': 'Register successful!'
            }, status=status.HTTP_201_CREATED)

        else:
            return JsonResponse({
                'error_message': 'This email has already exist!',
                'errors_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)


class CarrierViewSet(APIView):
    def post(self, request):
        serializer = CarrierLoginSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['isCarrier']==True :
                user = authenticate(
                    request,
                    username=serializer.validated_data['username'],
                    password=serializer.validated_data['password'],
                    isCarrier=serializer.validated_data['isCarrier'],
                )
                if user:
                    refresh = TokenObtainPairSerializer.get_token(user)
                    data = {
                        'refresh_token': str(refresh),
                        'access_token': str(refresh.access_token),
                        'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                        'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
                    }
                    return Response(data, status=status.HTTP_200_OK)

                return Response({
                    'error_message': 'Email or password is incorrect!',
                    'error_code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'failed': 'You havent permissions',
                    'status_code': 200
                }, status=status.HTTP_200_OK)
        return Response({
                'error_messages': serializer.errors,
                'error_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)


class TypeBusViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView):
    queryset = TypeBus.objects.filter(active=True)
    serializer_class = TypeBusSerializer

    @action(methods=['get'], detail=True, url_path='seat')
    def get_seat(self, request, pk):
        # course = Course.objects.get(pk=pk)
        typeBus = self.get_object()
        seat = Seat.objects.filter(typeBusID=typeBus.id, active=True)

        return Response(data=SeatSerializer(seat, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class BusViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset = Bus.objects.filter(active=True)
    serializer_class = BusSerializer
    pagination_class = BusPagination

    # tìm kiếm theo tên bus
    def get_queryset(self):
        list_bus = Bus.objects.filter(active=True)

        q = self.request.query_params.get('q')
        if q is not None:
            list_bus = list_bus.filter(name__icontains=q)

        # lọc theo rate
        rate = self.request.query_params.get('rate')
        if rate is not None:
            list_bus = list_bus.filter(rating=rate)

        return list_bus


class BusRouteViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView):
    queryset = BusRoute.objects.filter(active=True)
    serializer_class = BusRouteSerializer

    def get_permissions(self):
        if self.action in ['like', 'rating']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @swagger_auto_schema(
        operation_description='Get the comments of a BusRoute',
        responses={
            status.HTTP_200_OK: CommentSerializer()
        }
    )
    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        busroute = self.get_object()
        comments = busroute.comments.select_related('user')
        # comments = Comment.objects.filter(busroute == pk)

        return Response(CommentSerializer(comments, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='get-rating', detail=True)
    def get_rating(self, request, pk):
        busroute = self.get_object()
        rating = Rating.objects.filter(busroute=busroute)

        return Response(RatingSerializer(rating, many=True).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,
            url_path='last-comment')
    def last_book(self, request):
        lastComment = Comment.objects.all().last()
        return Response(data=CommentSerializer(lastComment,
                                               context={'request': request}).data,
                        status=status.HTTP_200_OK)


    @action(methods=['get'], detail=True, url_path='checked-user')
    def checked_user(self, request, pk):
        busroute = self.get_object()
        user = User.objects.filter(this_booking_user__timeTable__busRouteID__id=busroute.id)
        return Response(data=UserSerializer(user,many=True,
                                               context={'request': request}).data,
                        status=status.HTTP_200_OK)


class SeatViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = Seat.objects.filter(active=True)
    serializer_class = SeatSerializer


class TimeTableViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = TimeTable.objects.filter(active=True)
    serializer_class = TimeTableSerializer

    @action(methods=['get'], detail=True, url_path='booking')
    def get_seatt(self, request, pk):
        timetable = self.get_object()
        bookings= timetable.booking_timeTable.filter(active=True)

        bookings = bookings.filter(timeTable=timetable.id)

        return Response(data=BookingSerializer(bookings, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='garage')
    def get_garage(self, request, pk):
        timeTable = self.get_object().busRouteID.routeID.city_from.id
        garage = Garage.objects.filter(cityID=timeTable)

        return Response(data=GarageSerializer(garage, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='seat')
    def get_seat(self, request, pk):
        typeBus = TimeTable.objects.get(id=pk).busRouteID.busID.typeBusID.id
        timeTable = TimeTable.objects.get(id=pk).id
        booking = Booking.objects.filter(timeTable=timeTable)
        seat = []
        for b in booking:
            bookingDetail = BookingDetail.objects.filter(bookingID=b.id)
            for bd in bookingDetail:
                seat.append(bd.seatID.id)

        seat = Seat.objects.filter(typeBusID=typeBus).exclude(id__in=seat)

        return Response(data=SeatSerializer(seat, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='bookingdetails')
    def get_bookingdetail(self, request, pk):
        timetable = self.get_object()
        booking = Booking.objects.filter(timeTable=timetable.id)
        a = []
        for i in booking:
            a.append(i.id)
        booking_detail = BookingDetail.objects.filter(bookingID__in=a, active=True)

        return Response(data=BookingDetailSerializer(booking_detail, many=True,
                                                     context={'request': request}).data,
                        status=status.HTTP_200_OK)


class BookingViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView, generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = Booking.objects.filter(active=True)
    serializer_class = BookingSerializer

    @action(methods=['get'], detail=False,
            url_path='last-book')
    def last_book(self, request):
        lastBook = Booking.objects.all().last()
        return Response(data=BookingSerializer(lastBook,
                                               context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='seat')
    def get_seat(self, request, pk):
        typeBus = Booking.objects.get(id=pk).timeTable.busRouteID.busID.typeBusID.id
        seat = Seat.objects.filter(typeBusID=typeBus, active=True)

        return Response(data=SeatSerializer(seat,
                                               context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='booking-detail')
    def get_bookingdetail(self, request, pk):
        booking = self.get_object()
        booking_detail = BookingDetail.objects.filter(bookingID=booking.id, active=True)

        return Response(data=BookingDetailSerializer(booking_detail,many=True,
                                            context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='booking-delete')
    def booking_delete(self, request):
        booking = self.get_object().delete()
        booking_detail = BookingDetail.objects.filter(bookingID=booking.id, active=True)

        return Response(data=BookingDetailSerializer(booking_detail, many=True,
                                                     context={'request': request}).data,
                        status=status.HTTP_200_OK)


class BookingStatusViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView):
    queryset = BookingStatus.objects.filter(active=True)
    serializer_class = BookingStatusSerializer


class BookingHistoryViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView):
    queryset = BookingHistory.objects.filter(active=True)
    serializer_class = BookingHistorySerializer


class CityViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class DistrictViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class BookingDetailViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView):
    queryset = BookingDetail.objects.all()
    serializer_class = BookingDetailSerializer


class CommentViewSet(viewsets.ViewSet, generics.CreateAPIView,
                     generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = CreateCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [CommentOwnerPerms()]

        return [permissions.IsAuthenticated()]


class RatingViewSet(viewsets.ViewSet, generics.CreateAPIView,
                    generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [RatingOwnerPerms()]

        return [permissions.IsAuthenticated()]


class Momo(viewsets.ViewSet):
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    accessKey = "F8BBA842ECF85"
    secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    orderInfo = "MOMO"
    partnerCode = "MOMO"
    redirectUrl = "http://localhost:3000/MomoReturn"
    ipnUrl = "http://127.0.0.1:8000/"
    extraData = ""
    partnerName = "Bus station"
    requestType = "captureWallet"
    storeId = "Bus station"
    lang = "vi"
    @action(methods=['post'], detail=False, url_path='')
    def request_momo(self, request):
        if request.method == "POST":
            amount = str(request.data.get("amount"))
            self.orderInfo = str(request.data.get("name"))
            orderId = str(len(str(request.data.get("orderId")))) + '.' + str(uuid.uuid4()) + str(request.data.get("orderId"))
            requestId = str(len(str(request.data.get("orderId")))) + '.' + str(uuid.uuid4()) + str(request.data.get("orderId"))
            # rawSignature = "accessKey=" + self.accessKey + "&amount=" + amount  + "&extraData=" + self.extraData + "&ipnUrl=" + self.ipnUrl + "&orderId=" + orderId \
            #                + "&orderInfo=" + orderInfo + "&partnerCode=" + self.partnerCode + "&redirectUrl=" + self.redirectUrl \
            #                + "&requestId=" + requestId + "&requestType=" + self.requestType
            rawSignature = "accessKey=" + self.accessKey + "&amount=" + amount + "&extraData=" + self.extraData + "&ipnUrl=" + self.ipnUrl + "&orderId=" + orderId \
                           + "&orderInfo=" + self.orderInfo + "&partnerCode=" + self.partnerCode + "&redirectUrl=" + self.redirectUrl \
                           + "&requestId=" + requestId + "&requestType=" + self.requestType
            h = hmac.new(bytes(self.secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
            signature = h.hexdigest()
            data = {
                'partnerCode': self.partnerCode,
                'orderId': orderId,
                'partnerName': self.partnerName,
                'storeId': self.storeId,
                'ipnUrl': self.ipnUrl,
                'amount': amount,
                'lang': self.lang,
                'requestType': self.requestType,
                'redirectUrl': self.redirectUrl,
                'orderInfo': self.orderInfo,
                'requestId': requestId,
                'extraData': self.extraData,
                'signature': signature
            }
            data = json.dumps(data)
            print(data)
            clen = len(data)
            response = requests.post(self.endpoint, data=data,
                                     headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
            return Response(data=response.json(), status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='return-momo')
    def return_momo(self, request):
        if request.method == "POST":
            resultCode = request.data.get("resultCode")
            signature = str(request.data.get("signature"))
            message = request.data.get("message")
            responseTime = request.data.get("responseTime")
            transId = request.data.get("transId")
            orderType = request.data.get("orderType")
            payType = request.data.get("payType")
            amount = request.data.get("amount")
            self.orderInfo = str(request.data.get("name"))
            orderId = str(request.data.get("orderId"))
            requestId = request.data.get("requestId")
            if (resultCode == "0"):
                booking_history = BookingHistory.objects.filter(active=True, statusID=3).order_by('-bookingID')
                for d in booking_history:
                    selfOrderId = str(d.bookingID.id)
                    selfAmount = Booking.objects.get(id=d.bookingID.id)
                    print(selfAmount)
                    percentage = 0
                    if selfAmount.discount != None:
                        percentage = selfAmount.discount.percentage
                    quantity = len(BookingDetail.objects.filter(bookingID=d.bookingID.id))
                    if selfOrderId == orderId[-int(orderId[0:orderId.index('.')]):] \
                            and float(amount) == selfAmount.timeTable.busRouteID.price * quantity * (1 - percentage):
                        raw = "accessKey=" + self.accessKey + "&amount=" + amount  +\
                              "&extraData=" + self.extraData + "&message=" + message + \
                              "&orderId=" + orderId + "&orderInfo=" + self.orderInfo + \
                              "&orderType=" + orderType + "&partnerCode=" + self.partnerCode + \
                              "&payType=" + payType + "&requestId=" + requestId + \
                              "&responseTime=" + responseTime + \
                              "&resultCode=" + resultCode + "&transId=" + transId
                        selfSignature = str(hmac.new(bytes(self.secretKey, 'ascii'), bytes(raw, 'utf-8'), hashlib.sha256).hexdigest())
                        print(signature, selfSignature)
                        if(signature == selfSignature):
                            try:
                                d.statusID = BookingStatus.objects.get(id=1)
                                d.save()
                            except Exception as ex:
                                print(ex)
                                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
                            return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
#
# class Momo(viewsets.ViewSet):
#     @action(methods=['post'], detail=False, url_path='')
#     def request_momo(self, request):
#         endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
#         partnerCode = "MOMO"
#         accessKey = "F8BBA842ECF85"
#         secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
#
#
#         #quay về trang cân quay về
#         redirectUrl = "http://127.0.0.1:8000/"
#         #mô tả thông tin đơn hàng
#         orderInfo = "Bus Station"
#         #ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
#         ipnUrl = "http://127.0.0.1:8000/"
#         orderId = str(uuid.uuid4())
#         requestId = str(uuid.uuid4())
#         requestType = "captureWallet"
#         extraData = ""  # pass empty value or Encode base64 JsonString
#
#         # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
#         # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
#         # &requestType=$requestType
#         if request.method == "POST":
#             amount = str(request.data.get("amount"))
#             name = str(request.data.get("name"))
#             info = str(request.data.get("info"))
#             orderInfo = name + "\n" + info
#             rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType
#
#         # puts raw signature
#         print("--------------------RAW SIGNATURE----------------")
#         print(rawSignature)
#         # signature
#         h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
#         signature = h.hexdigest()
#         print("--------------------SIGNATURE----------------")
#         print(signature)
#
#         # json object send to MoMo endpoint
#
#         data = {
#             'partnerCode': partnerCode,
#             'partnerName': "Test",
#             'storeId': "MomoTestStore",
#             'requestId': requestId,
#             'amount': amount,
#             'orderId': orderId,
#             'orderInfo': orderInfo,
#             'redirectUrl': redirectUrl,
#             'ipnUrl': ipnUrl,
#             'lang': "vi",
#             'extraData': extraData,
#             'requestType': requestType,
#             'signature': signature
#         }
#         print("--------------------JSON REQUEST----------------\n")
#         data = json.dumps(data)
#         print(data)
#
#         clen = len(data)
#         response = requests.post(endpoint, data=data,
#                                  headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
#
#         return Response(data=response.json(), status=status.HTTP_200_OK)