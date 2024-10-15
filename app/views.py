from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Road, Payment, RoadPayment


def index(request):
    road_name = request.GET.get("road_name", "")
    roads = Road.objects.filter(status=1)

    if road_name:
        roads = roads.filter(name__icontains=road_name)

    draft_payment = get_draft_payment()

    context = {
        "road_name": road_name,
        "roads": roads
    }

    if draft_payment:
        context["roads_count"] = len(draft_payment.get_roads())
        context["draft_payment"] = draft_payment

    return render(request, "roads_page.html", context)


def add_road_to_draft_payment(request, road_id):
    road = Road.objects.get(pk=road_id)

    draft_payment = get_draft_payment()

    if draft_payment is None:
        draft_payment = Payment.objects.create()
        draft_payment.owner = get_current_user()
        draft_payment.date_created = timezone.now()
        draft_payment.save()

    if RoadPayment.objects.filter(payment=draft_payment, road=road).exists():
        return redirect("/")

    item = RoadPayment(
        payment=draft_payment,
        road=road
    )
    item.save()

    return redirect("/")


def road_details(request, road_id):
    context = {
        "road": Road.objects.get(id=road_id)
    }

    return render(request, "road_page.html", context)


def delete_payment(request, payment_id):
    if not Payment.objects.filter(pk=payment_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE payments SET status=5 WHERE id = %s", [payment_id])

    return redirect("/")


def payment(request, payment_id):
    if not Payment.objects.filter(pk=payment_id).exists():
        return redirect("/")

    payment = Payment.objects.get(id=payment_id)
    if payment.status == 5:
        return redirect("/")

    context = {
        "payment": payment,
    }

    return render(request, "payment_page.html", context)


def get_draft_payment():
    return Payment.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()