from rest_framework import serializers

from .models import *


class RoadsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, road):
        if road.image:
            # Получить URL изображения
            url = road.image.url.replace("minio", "localhost", 1)

            # Найти начало параметров запроса (знак '?') и обрезать их
            url_without_params = url.split('?')[0]

            return url_without_params

        # Вернуть ссылку на изображение по умолчанию
        return "http://localhost:9000/images/default.png"


    class Meta:
        model = Road
        fields = ("id", "name", "status", "speed", "image")


class RoadSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, road):
        if road.image:
            # Получить URL изображения
            url = road.image.url.replace("minio", "localhost", 1)

            # Найти начало параметров запроса (знак '?') и обрезать их
            url_without_params = url.split('?')[0]

            return url_without_params


    class Meta:
        model = Road
        fields = ['name', 'description', 'status', 'image', 'speed', 'start', 'end']

    def validate_start(self, value):
        if value is None:
            raise serializers.ValidationError("Поле 'start' обязательно для заполнения.")
        return value

    def validate_end(self, value):
        if value is None:
            raise serializers.ValidationError("Поле 'end' обязательно для заполнения.")
        return value

class PaymentsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentSerializer(PaymentsSerializer):
    roads = serializers.SerializerMethodField()

    def get_roads(self, payment):
        items = RoadPayment.objects.filter(payment=payment)
        return [RoadItemSerializer(item.road, context={"day_night": item.day_night}).data for item in items]


class RoadItemSerializer(RoadSerializer):
    day_night = serializers.SerializerMethodField()

    def get_day_night(self, road):
        return self.context.get("day_night")

    class Meta(RoadSerializer.Meta):
        fields = "__all__"


class RoadPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadPayment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
