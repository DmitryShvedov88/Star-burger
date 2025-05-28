from django.db import models


class Place(models.Model):
    address = models.CharField(
        max_length=250,
        verbose_name="Адрес",
        unique=True
    )
    longitude = models.FloatField(
        verbose_name="Долгота",
        blank=True,
        null=True
    )
    latitude = models.FloatField(
        verbose_name="Широта",
        blank=True,
        null=True
    )
    request_time = models.TimeField(
        auto_now=True,
        verbose_name="Время запроса",
    )

    def __str__(self):
        return self.address