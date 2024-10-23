import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta, random_bool


def add_users():
    User.objects.create_user("user", "user@user.com", "1234")
    User.objects.create_superuser("root", "root@root.com", "1234")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234")

    print("Пользователи созданы")


def add_roads():
    Road.objects.create(
        name="М-1 'Беларусь'",
        description="М-1 «Беларусь» берет начало на пересечении Можайского шоссе и МКАД и ведёт до государственной границы с Республикой Беларусь. Также М-1 является частью европейского маршрута E30 и азиатского маршрута AH6. В оперативном управлении Государственной компании «Автодор» находится участок с 17-го по 456-й километр. Государственная компания осуществляет комплексную реконструкцию автодороги М-1 «Беларусь» с доведением параметров трассы до норм высшей технической категории.",
        speed=110,
        start=130,
        end=280,
        image="1.png"
    )

    Road.objects.create(
        name="М-3 'Украина'",
        description="В 1938 году было начато проектирование автодороги, получившей тогда наименование «Москва — Севск».За период с 1964-го по 1976-й годы осуществлена реконструкция автодороги с устройством цементобетонного покрытия, достроены и восстановлены 23 малых искусственных сооружения, на участке реконструкции 106-й — 110-й",
        speed=100,
        start=50,
        end=130,
        image="2.png"
    )

    Road.objects.create(
        name="М-4 'Дон'",
        description="М-4 «Дон» – ключевая транспортная артерия юга России. Автодорога проходит по территории Московской, Тульской, Липецкой, Воронежской, Ростовской областей, Республики Адыгея и Краснодарского края.",
        speed=90,
        start=70,
        end=180,
        image="3.png"
    )

    Road.objects.create(
        name="М-11 'Нева'",
        description="Скоростная автомобильная дорога М-11 «Нева» протянулась от Московской кольцевой автомобильной дороги до примыкания к Кольцевой автомобильной дороге вокруг Санкт-Петербурга. Автодорога проходит по территориям Центрального и Северо-западного федеральных округов, по Московской, Тверской, Новгородской и Ленинградской областям в обход всех населенных пунктов.",
        speed=130,
        start=200,
        end=290,
        image="4.png"
    )

    Road.objects.create(
        name="М-12 'Восток'",
        description="Скоростная автомобильная дорога М-12 «Восток» является частью международного транспортного маршрута «Европа - Западный Китай». Протяженность трассы составляет более 800 км, полностью движение по ней от Москвы до Казани было открыто в конце 2023 года.",
        speed=120,
        start=250,
        end=360,
        image="5.png"
    )

    Road.objects.create(
        name="ЦКАД",
        description="Центральная кольцевая автодорога – самый масштабный на сегодняшний день проект в области дорожной инфраструктуры в Московском регионе. Новая трасса призвана стать основой опорной сети скоростных автодорог России и частью международных транспортных коридоров. Проект реализуется на принципах ГЧП.",
        speed=110,
        start=170,
        end=320,
        image="6.png"
    )

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_payments():
    users = User.objects.filter(is_superuser=False)
    moderators = User.objects.filter(is_superuser=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    roads = Road.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        add_payment(status, roads, users, moderators)

    add_payment(1, roads, users, moderators)

    print("Заявки добавлены")


def add_payment(status, roads, users, moderators):
    payment = Payment.objects.create()
    payment.status = status

    if payment.status in [3, 4]:
        payment.date_complete = random_date()
        payment.date_formation = payment.date_complete - random_timedelta()
        payment.date_created = payment.date_formation - random_timedelta()
    else:
        payment.date_formation = random_date()
        payment.date_created = payment.date_formation - random_timedelta()

    payment.owner = random.choice(users)
    payment.moderator = random.choice(moderators)

    payment.date = random_date()
    payment.number = "A777AA777"

    for road in random.sample(list(roads), 3):
        item = RoadPayment(
            payment=payment,
            road=road,
            value=random_bool()
        )
        item.save()

    payment.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_roads()
        add_payments()
