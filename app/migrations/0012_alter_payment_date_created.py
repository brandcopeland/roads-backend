# Generated by Django 4.2.7 on 2024-10-22 20:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_payment_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 22, 20, 57, 40, 559192, tzinfo=datetime.timezone.utc), verbose_name='Дата создания'),
        ),
    ]