from django.db import models


class City(models.Model):
    """Город"""

    name = models.CharField(verbose_name="Название города", unique=True, max_length=150)
    count = models.IntegerField(
        verbose_name="Сколько раз искали этот город", blank=True, null=False, default=1
    )

    def __str__(self):
        return self.name
