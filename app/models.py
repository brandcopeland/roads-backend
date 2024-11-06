from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Road(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    speed = models.IntegerField(verbose_name="Разрешенная скорость")
    start = models.IntegerField(verbose_name="Начальное значение")
    end = models.IntegerField(verbose_name="Конечное значение")

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
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Сотрудник", related_name='moderator', blank=True,  null=True)

    date = models.DateField(blank=True, null=True)
    number = models.CharField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return "Оплат №" + str(self.pk)

    class Meta:
        verbose_name = "Оплат"
        verbose_name_plural = "Оплаты"
        db_table = "payments"
        ordering = ('-date_formation', )


class RoadPayment(models.Model):
    road = models.ForeignKey(Road, on_delete=models.DO_NOTHING, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.DO_NOTHING, blank=True, null=True)
    day_night = models.BooleanField(verbose_name="Поле м-м", default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "road_payment"
        constraints = [
            models.UniqueConstraint(fields=['road', 'payment'], name="road_payment_constraint")
        ]
