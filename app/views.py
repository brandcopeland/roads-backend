import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .management.commands.fill_db import calc
from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_payment(request):
    user = identity_user(request)

    if user is None:
        return None

    payment = Payment.objects.filter(owner=user).filter(status=1).first()

    return payment


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'query',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_roads(request):
    road_name = request.GET.get("road_name", "")

    roads = Road.objects.filter(status=1)

    if road_name:
        roads = roads.filter(name__icontains=road_name)

    serializer = RoadsSerializer(roads, many=True)

    draft_payment = get_draft_payment(request)

    resp = {
        "roads": serializer.data,
        "roads_count": RoadPayment.objects.filter(payment=draft_payment).count() if draft_payment else None,
        "draft_payment_id": draft_payment.pk if draft_payment else None
    }

    return Response(resp)


# @api_view(["GET"])
# def get_road_by_id(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)
    serializer = RoadSerializer(road)

    return Response(serializer.data)

from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
def get_road_by_id(request, road_id):
    # Выполнение SQL-запроса напрямую
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM public.roads
            WHERE id = %s
        """, [road_id])
        row = cursor.fetchone()

    # Проверка на существование дороги
    if not row:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Подготовка ответа
    road_data = {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "status": row[3],
        "image": "http://localhost:9000/images/"+row[4] if row[4] else "http://localhost:9000/images/default.png",
        "speed": row[5],
        "start": row[6],
        "end": row[7],
    }
    return Response(road_data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_road(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)

    serializer = RoadSerializer(road, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_road(request):
    serializer = RoadSerializer(data=request.data, partial=False)
    
    # Проверка данных
    serializer.is_valid(raise_exception=True)
    
    # Сохранение объекта
    serializer.save()
    
    # Получение и сериализация всех объектов
    roads = Road.objects.filter(status=1)
    serializer = RoadSerializer(roads, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_road(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)
    road.status = 2
    road.save()

    road = Road.objects.filter(status=1)
    serializer = RoadSerializer(road, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_road_to_payment(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)

    draft_payment = get_draft_payment(request)

    if draft_payment is None:
        draft_payment = Payment.objects.create()
        draft_payment.date_created = timezone.now()
        draft_payment.owner = identity_user(request)
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
@permission_classes([IsModerator])
def update_road_image(request, road_id):
    if not Road.objects.filter(pk=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    road = Road.objects.get(pk=road_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    road.image = image
    road.save()

    serializer = RoadSerializer(road)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_payments(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    payments = Payment.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        payments = payments.filter(owner=user)

    if status_id > 0:
        payments = payments.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        payments = payments.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        payments = payments.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = PaymentsSerializer(payments, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_payment_by_id(request, payment_id):
    user = identity_user(request)

    if not Payment.objects.filter(pk=payment_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.get(pk=payment_id)
    serializer = PaymentSerializer(payment)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=PaymentSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_payment(request, payment_id):
    user = identity_user(request)

    if not Payment.objects.filter(pk=payment_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.get(pk=payment_id)
    serializer = PaymentSerializer(payment, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, payment_id):
    user = identity_user(request)

    if not Payment.objects.filter(pk=payment_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.get(pk=payment_id)

    if payment.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    payment.status = 2
    payment.date_formation = timezone.now()
    payment.save()

    serializer = PaymentSerializer(payment)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, payment_id):
    if not Payment.objects.filter(pk=payment_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    payment = Payment.objects.get(pk=payment_id)

    if payment.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        payment.time = calc()

    payment.status = request_status
    payment.date_complete = timezone.now()
    payment.moderator = identity_user(request)
    payment.save()

    serializer = PaymentSerializer(payment)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_payment(request, payment_id):
    user = identity_user(request)

    if not Payment.objects.filter(pk=payment_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.get(pk=payment_id)

    if payment.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    payment.status = 5
    payment.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_road_from_payment(request, payment_id, road_id):
    user = identity_user(request)

    if not Payment.objects.filter(pk=payment_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not RoadPayment.objects.filter(payment_id=payment_id, road_id=road_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = RoadPayment.objects.get(payment_id=payment_id, road_id=road_id)
    item.delete()

    payment = Payment.objects.get(pk=payment_id)

    serializer = PaymentSerializer(payment)
    roads = serializer.data["roads"]

    return Response(roads)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_road_payment(request, payment_id, road_id):
    user = identity_user(request)

    if not Payment.objects.filter(pk=payment_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not RoadPayment.objects.filter(road_id=road_id, payment_id=payment_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = RoadPayment.objects.get(road_id=road_id, payment_id=payment_id)

    serializer = RoadPaymentSerializer(item)

    return Response(serializer.data)


@swagger_auto_schema(method='PUT', request_body=RoadPaymentSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_road_in_payment(request, payment_id, road_id):
    user = identity_user(request)

    if not Payment.objects.filter(pk=payment_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not RoadPayment.objects.filter(road_id=road_id, payment_id=payment_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = RoadPayment.objects.get(road_id=road_id, payment_id=payment_id)

    serializer = RoadPaymentSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
