from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from .register import register_social_user
from . import  google, facebook
from .models import *


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class DistrictSerializer(serializers.ModelSerializer):
    cityID = CitySerializer()

    class Meta:
        model = District
        fields = ['id', 'name', 'cityID']


class GarageSerializer(serializers.ModelSerializer):
    cityID = CitySerializer()
    districtID = DistrictSerializer()

    class Meta:
        model = Garage
        fields = ['id', 'name', 'address', 'cityID', 'districtID']


class UserSerializer(serializers.ModelSerializer):
    avatar_path = serializers.SerializerMethodField(source='avatar')

    def get_avatar_path(self, obj):
        request = self.context.get('request')
        if obj.avatar and not obj.avatar.name.startswith('/static'):
            path = '/static/%s' % obj.avatar.name
            print(request, path)
            return request.build_absolute_uri(path)
            # return 1

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'password', 'email', 'phone',
                  'avatar', 'avatar_path', 'isCarrier']
        extra_kwargs = {
            'password': {
                'write_only': True
            }, 'avatar_path': {
                'read_only': True
            }, 'avatar': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()

        return user


class CarrierLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    isCarrier = serializers.BooleanField(required=True)


class RouteSerializer(serializers.ModelSerializer):
    city_from = CitySerializer()
    to_garage = GarageSerializer()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and not obj.image.name.startswith('/static'):
            path = '/static/%s' % obj.image.name
            return request.build_absolute_uri(path)

    class Meta:
        model = Route
        fields = '__all__'


class TypeBusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeBus
        fields = ['id', 'name']


class BusSerializer(serializers.ModelSerializer):
    typeBusID = TypeBusSerializer()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and not obj.image.name.startswith('/static'):
            path = '/static/%s' % obj.image.name
            return request.build_absolute_uri(path)

    class Meta:
        model = Bus
        fields = '__all__'


class BusRouteSerializer(serializers.ModelSerializer):
    busID = BusSerializer()
    routeID = RouteSerializer()
    rate = SerializerMethodField()

    def get_rate(self, busroute):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            r = busroute.rating_set.filter(user=request.user).first()
            if r:
                return r.rate
        return -1

    class Meta:
        model = BusRoute
        fields = ['id', 'price', 'busID', 'routeID', 'rate']


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'active', 'location', 'typeBusID']


class TimeTableSerializer(serializers.ModelSerializer):
    busRouteID = BusRouteSerializer()

    class Meta:
        model = TimeTable
        fields = ['id', 'date', 'time', 'busRouteID']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'customerID', 'name', 'phone', 'timeTable']


class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingStatus
        fields = ['id', 'statusValue']


class BookingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingHistory
        fields = ['id', 'bookingID', 'statusID', 'statusDate']


class BookingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDetail
        fields = ['id', 'bookingID', 'from_garage', 'seatID']


class AuthBusRouteSerializer(BusRouteSerializer):
    like = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def get_like(self, busroute):
        request = self.context.get('request')
        if request:
            return busroute.like_set.filter(user=request.user, active=True).exists()

    def get_rating(self, busroute):
        request = self.context.get('request')
        if request:
            r = busroute.rating_set.filter(user=request.user).first()
            if r:
                return r.rate

    class Meta:
        model = BusRoute
        fields = BusRouteSerializer.Meta.fields + ['like', 'rating']


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'busroute']


class BookingDetailReadSerializer(serializers.ModelSerializer):
    from_garage = GarageSerializer(read_only=True)
    seatID = SeatSerializer(read_only=True)

    class Meta:
        model = BookingDetail
        fields = ['id', 'bookingID', 'from_garage', 'seatID']


class UserAuthSerializer(UserSerializer):
    avatar_path = serializers.SerializerMethodField(source='avatar')

    def get_avatar_path(self, obj):
        request = self.context.get('request')
        if obj.avatar and not obj.avatar.name.startswith('/static'):
            path = '/static/%s' % obj.avatar.name
            return request.build_absolute_uri(path)
            # return 1

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar_path']
        extra_kwargs = {
            'avatar_path': {
                'read_only': True
            }
        }


class CommentSerializer(serializers.ModelSerializer):
    user = UserAuthSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_date', 'updated_date', 'user']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'busroute', 'rate', 'user', 'comment']


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        # if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
        #     raise AuthenticationFailed('we cannot authenticate for you!!!')
        email = user_data['email']
        name = user_data['email']
        provider = 'google'

        return register_social_user(
            provider=provider, email=email, name=name)


class FacebookSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = facebook.Facebook.validate(auth_token)

        try:
        # user_id = user_data['id']
            email = user_data['email']
            name = user_data['name']
            provider = 'facebook'
            return register_social_user(
                provider=provider,
                # user_id=user_id,
                email=email,
                name=name
            )
        except Exception:

            raise serializers.ValidationError(
                'The token  is invalid or expired. Please login again.'
            )