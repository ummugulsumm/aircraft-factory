from django.db import models


class AircraftTypes(models.IntegerChoices):
    TB2 = 1, 'TB2'
    TB3 = 2, 'TB3'
    AKINCI = 3, 'AKINCI'
    KIZILELMA = 4, 'KIZILELMA'