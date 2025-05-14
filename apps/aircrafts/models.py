from django.db import models
from django.utils.translation import gettext_lazy as _
from common.mixins import TimestampMixin
from apps.teams.models import Personnel
from common.utils import generate_aircraft_serial_number
from apps.aircrafts.enums import AircraftTypes

class Aircraft(TimestampMixin):
    
    aircraft_type = models.PositiveSmallIntegerField(
        _("Aircraft Type"),
        choices=AircraftTypes.choices
    )
    serial_number = models.CharField(
        _("Serial Number"),
        max_length=100,
        unique=True,
        blank=True
    )
    assembly_date = models.DateTimeField(_("Assembly Date"), auto_now_add=True)
    assembled_by = models.ForeignKey(
        Personnel, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='assembled_aircrafts',
        verbose_name=_("Assembled By")
    )
    
    class Meta:
        verbose_name = _("Aircraft")
        verbose_name_plural = _("Aircraft")
        indexes = [
            models.Index(fields=['aircraft_type']),
        ]

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = generate_aircraft_serial_number(
                AircraftTypes(self.aircraft_type).label
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_aircraft_type_display()} - {self.serial_number}"