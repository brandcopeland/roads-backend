import requests
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_payment():
    return Payment.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_roads(request):
    road_name = request.GET.get("road_name", "")

    roads = Road.objects.filter(status=1)

    if road_name:
        roads = roads.filter(name__icontains=road_name)

    serializer = RoadSerializer(roads, many=True)

    draft_payment = get_draft_payment()

    resp = {
        "roads": serializer.data,
        "roads_count": len(serializer.data),
        "draft_payment": draft_payment.pk if draft_payment else None
    }

    return Response(resp)


@api_view(["GET"])
def get_road_by_id(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)
    serializer = RoadSerializer(road, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_road(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)

    image = request.data.get("image")
    if image is not None:
        road.image = image
        road.save()

    serializer = RoadSerializer(road, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_road(request):
    road = Road(**request.data)
    road.save()

    roads = Road.objects.filter(status=1)
    serializer2 = RoadSerializer(roads, many=True)

    return Response(serializer2.data)


@api_view(["DELETE"])
def delete_road(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)
    road.status = 2
    road.save()

    roads = Road.objects.filter(status=1)
    serializer = RoadSerializer(roads, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_road_to_payment(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)

    draft_payment = get_draft_payment()

    if draft_payment is None:
        draft_payment = Payment.objects.create()
        draft_payment.owner = get_user()
        draft_payment.date_created = timezone.now()
        draft_payment.save()

    if RoadPayment.objects.filter(payment=draft_payment, road=road).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = RoadPayment.objects.create()
    item.payment = draft_payment
    item.road = road
    item.save()

    serializer = PaymentSerializer(draft_payment)
    return Response(serializer.data["roads"])


@api_view(["POST"])
def update_road_image(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)

    image = request.data.get("image")
    if image is not None:
        road.image = image
        road.save()

    serializer = RoadSerializer(road)

    return Response(serializer.data)


@api_view(["GET"])
def search_payments(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    payments = Payment.objects.exclude(status__in=[1, 5])

    if status > 0:
        payments = payments.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        payments = payments.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        payments = payments.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = PaymentsSerializer(payments, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_payment_by_id(request, payment_id):
    if not Payment.objects.filter(pk=payment_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.get(pk=payment_id)
    serializer = PaymentSerializer(payment, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_payment(request, payment_id):
    if not Payment.objects.filter(pk=payment_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.get(pk=payment_id)
    serializer = PaymentSerializer(payment, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, payment_id):
    if not Payment.objects.filter(pk=payment_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.get(pk=payment_id)

    if payment.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    payment.status = 2
    payment.date_formation = timezone.now()
    payment.save()

    serializer = PaymentSerializer(payment, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, payment_id):
    if not Payment.objects.filter(pk=payment_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    payment = Payment.objects.get(pk=payment_id)

    if payment.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    payment.date_complete = timezone.now()
    payment.status = request_status
    payment.moderator = get_moderator()
    payment.save()

    serializer = PaymentSerializer(payment, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_payment(request, payment_id):
    if not Payment.objects.filter(pk=payment_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.get(pk=payment_id)

    if payment.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    payment.status = 5
    payment.save()

    serializer = PaymentSerializer(payment, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_road_from_payment(request, payment_id, road_id):
    if not RoadPayment.objects.filter(payment_id=payment_id, road_id=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = RoadPayment.objects.get(payment_id=payment_id, road_id=road_id)
    item.delete()

    payment = Payment.objects.get(pk=payment_id)

    serializer = PaymentSerializer(payment, many=False)
    roads = serializer.data["roads"]

    if len(roads) == 0:
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(roads)


@api_view(["PUT"])
def update_road_in_payment(request, payment_id, road_id):
    if not RoadPayment.objects.filter(road_id=road_id, payment_id=payment_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = RoadPayment.objects.get(road_id=road_id, payment_id=payment_id)

    serializer = RoadPaymentSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)