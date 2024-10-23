from rest_framework import serializers

from .models import *


class RoadSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, road):
        if road.image:
            return road.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Road
        fields = "__all__"


class RoadItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_image(self, road):
        if road.image:
            return road.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    def get_value(self, road):
        return self.context.get("value")

    class Meta:
        model = Road
        fields = ("id", "name", "image", "value")


class PaymentSerializer(serializers.ModelSerializer):
    roads = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, payment):
        return payment.owner.username

    def get_moderator(self, payment):
        if payment.moderator:
            return payment.moderator.username
            
    def get_roads(self, payment):
        items = RoadPayment.objects.filter(payment=payment)
        return [RoadItemSerializer(item.road, context={"value": item.value}).data for item in items]

    class Meta:
        model = Payment
        fields = '__all__'


class PaymentsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, payment):
        return payment.owner.username

    def get_moderator(self, payment):
        if payment.moderator:
            return payment.moderator.username

    class Meta:
        model = Payment
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
