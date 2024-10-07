from django.shortcuts import render

roads = [
    {
        "id": 1,
        "name": "М-1 'Беларусь'",
        "description": "М-1 «Беларусь» берет начало на пересечении Можайского шоссе и МКАД и ведёт до государственной границы с Республикой Беларусь. Также М-1 является частью европейского маршрута E30 и азиатского маршрута AH6. В оперативном управлении Государственной компании «Автодор» находится участок с 17-го по 456-й километр. Государственная компания осуществляет комплексную реконструкцию автодороги М-1 «Беларусь» с доведением параметров трассы до норм высшей технической категории.",
        "speed": 110,
        "start_value":130,
        "end_value":280,
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "М-3 'Украина'",
        "description": "В 1938 году было начато проектирование автодороги, получившей тогда наименование «Москва — Севск».За период с 1964-го по 1976-й годы осуществлена реконструкция автодороги с устройством цементобетонного покрытия, достроены и восстановлены 23 малых искусственных сооружения, на участке реконструкции 106-й — 110-й",
        "speed": 100,
        "start_value":300,
            "end_value":800,
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "М-4 'Дон'",
        "description": "М-4 «Дон» – ключевая транспортная артерия юга России. Автодорога проходит по территории Московской, Тульской, Липецкой, Воронежской, Ростовской областей, Республики Адыгея и Краснодарского края.",
        "speed": 90,
        "start_value":50,
            "end_value":140,
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "М-11 'Нева'",
        "description": "Скоростная автомобильная дорога М-11 «Нева» протянулась от Московской кольцевой автомобильной дороги до примыкания к Кольцевой автомобильной дороге вокруг Санкт-Петербурга. Автодорога проходит по территориям Центрального и Северо-западного федеральных округов, по Московской, Тверской, Новгородской и Ленинградской областям в обход всех населенных пунктов.",
        "speed": 130,
        "start_value":10,
        "end_value":200,
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "М-12 'Восток'",
        "description": "Скоростная автомобильная дорога М-12 «Восток» является частью международного транспортного маршрута «Европа - Западный Китай». Протяженность трассы составляет более 800 км, полностью движение по ней от Москвы до Казани было открыто в конце 2023 года.",
        "speed": 120,
        "start_value":123,
            "end_value":289,
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "ЦКАД",
        "description": "Центральная кольцевая автодорога – самый масштабный на сегодняшний день проект в области дорожной инфраструктуры в Московском регионе. Новая трасса призвана стать основой опорной сети скоростных автодорог России и частью международных транспортных коридоров. Проект реализуется на принципах ГЧП.",
        "speed": 110,
        "start_value":20,
            "end_value":180,
        "image": "http://localhost:9000/images/6.png"
    }
]

payments = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "date": "28 сентября 2024г",
    "car_number":"А777АА777",
    "roads": [
        {
            "id": 1,
            "start_value":130,
            "end_value":280,
            "time_of_day":"День",
        },
        {
            "id": 2,
            "start_value":30,
            "end_value":230,
            "time_of_day":"Ночь",
        },
        {
            "id": 3,
            "start_value":0,
            "end_value":150,
            "time_of_day":"День",
        }
    ]
}


def getRoadById(road_id):
    for road in roads:
        if road["id"] == road_id:
            return road


def getRoads():
    return roads


def searchRoads(road_name):
    res = []

    for road in roads:
        if road_name.lower() in road["name"].lower():
            res.append(road)

    return res


def getPayments():
    return payments


def getPaymentById(payment_id):
    return payments


def index(request):
    road_name = request.GET.get("road_name", "")
    roads = searchRoads(road_name) if road_name else getRoads()
    payments = getPayments()

    context = {
        "roads": roads,
        "road_name": road_name,
        "roads_count": len(payments["roads"]),
        "payments": payments
    }

    return render(request, "home_page.html", context)


def road(request, road_id):
    context = {
        "id": road_id,
        "road": getRoadById(road_id),
    }

    return render(request, "road_page.html", context)


def payment(request, payment_id):
    payment = getPaymentById(payment_id)
    roads = [
        {**getRoadById(road["id"]), "start_value": road["start_value"],"end_value": road["end_value"], "time_of_day":road["time_of_day"]}
        for road in payment["roads"]
    ]

    context = {
        "payment": payment,
        "roads": roads
    }

    return render(request, "payment_page.html", context)
