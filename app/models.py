from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Road(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название", blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(default="default.png", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)

    speed = models.IntegerField(blank=True)
    start = models.IntegerField(blank=True)
    end = models.IntegerField(blank=True)

    def get_image(self):
        return self.image.url.replace("minio", "localhost", 1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Дорога"
        verbose_name_plural = "Дороги"
        db_table = "roads"


class Payment(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True,
                              related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор", null=True,
                                  related_name='moderator')

    date = models.DateField(blank=True, null=True)
    number = models.CharField(blank=True, null=True)

    def __str__(self):
        return "Оплата №" + str(self.pk)

    def get_roads(self):
        return [
            setattr(item.road, "value", item.value) or item.road
            for item in RoadPayment.objects.filter(payment=self)
        ]

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"
        ordering = ('-date_formation',)
        db_table = "payments"


class RoadPayment(models.Model):
    road = models.ForeignKey(Road, models.DO_NOTHING, blank=True, null=True)
    payment = models.ForeignKey(Payment, models.DO_NOTHING, blank=True, null=True)
    value = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "road_payment"
        unique_together = ('road', 'payment')
