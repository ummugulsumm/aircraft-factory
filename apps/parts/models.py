from django.db import models
from django.utils.translation import gettext_lazy as _
from common.mixins import TimestampMixin
from apps.teams.models import Team, Personnel
from apps.aircrafts.models import Aircraft
from common.utils import generate_part_serial_number
from apps.parts.enums import PartTypes, PartStatus, InventoryStatus
from apps.aircrafts.enums import AircraftTypes
from django.core.validators import MinValueValidator


class Part(TimestampMixin):

    status = models.PositiveSmallIntegerField(
        choices=PartStatus.choices,
        default=PartStatus.AVAILABLE,
        verbose_name=_("Status")
    )
    part_type = models.PositiveSmallIntegerField(
        _("Part Type"), 
        choices=PartTypes.choices
    )
    aircraft_type = models.PositiveSmallIntegerField(_("Aircraft Type"), choices=AircraftTypes.choices)
    serial_number = models.CharField(_("Serial Number"), max_length=100, unique=True, blank=True)
    produced_by = models.ForeignKey(
        Personnel, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='produced_parts',
        verbose_name=_("Produced By")
    )

    class Meta:
        verbose_name = _("Part")
        verbose_name_plural = _("Parts")
        indexes = [
            models.Index(fields=['part_type', 'aircraft_type']),
            models.Index(fields=['status']),
        ]

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = generate_part_serial_number(
                PartTypes(self.part_type).label, 
                AircraftTypes(self.aircraft_type).label
            )
        super().save(*args, **kwargs)

    def __str__(self):
        aircraft_name = AircraftTypes(self.aircraft_type).label
        part_name = PartTypes(self.part_type).label
        return f"{aircraft_name} {part_name} - {self.serial_number}"


class UsedPart(TimestampMixin):

    part = models.OneToOneField(
        Part, 
        on_delete=models.CASCADE, 
        related_name='usage',
        verbose_name=_("Part")
    )
    aircraft = models.ForeignKey(
        Aircraft, 
        on_delete=models.CASCADE, 
        related_name='used_parts',
        verbose_name=_("Aircraft")
    )
    used_by = models.ForeignKey(
        Personnel, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='used_parts',
        verbose_name=_("Used By")
    )
    
    class Meta:
        verbose_name = _("Used Part")
        verbose_name_plural = _("Used Parts")

    def __str__(self):
        return _("Part {0} used in: {1}").format(self.part.serial_number, self.aircraft.serial_number)


class Inventory(TimestampMixin):

    part_type = models.PositiveSmallIntegerField(
        _("Part Type"), 
        choices=PartTypes.choices
    )
    aircraft_type = models.IntegerField(_("Aircraft Type"), choices=AircraftTypes.choices)
    quantity = models.PositiveIntegerField(_("Quantity"), default=0)
    inventory_status = models.PositiveSmallIntegerField(
        _("Inventory Status"),
        choices=InventoryStatus.choices,
        default=InventoryStatus.ADEQUATE
    )
    threshold_low = models.PositiveIntegerField(_("Low Stock Threshold"), default=5)
    threshold_critical = models.PositiveIntegerField(_("Critical Stock Threshold"), default=2)

    class Meta:
        verbose_name = _("Inventory")
        verbose_name_plural = _("Inventories")
        unique_together = ('part_type', 'aircraft_type')
        indexes = [
            models.Index(fields=['inventory_status']),
        ]

    def save(self, *args, **kwargs):
        self.update_inventory_status()
        super().save(*args, **kwargs)

    def update_inventory_status(self):

        if self.quantity == 0:
            self.inventory_status = InventoryStatus.OUT_OF_STOCK
        elif self.quantity <= self.threshold_critical:
            self.inventory_status = InventoryStatus.CRITICAL
        elif self.quantity <= self.threshold_low:
            self.inventory_status = InventoryStatus.LOW
        else:
            self.inventory_status = InventoryStatus.ADEQUATE

    def __str__(self):
        aircraft_name = AircraftTypes(self.aircraft_type).label
        part_name = PartTypes(self.part_type).label
        return _("{0} {1} - {2} units ({3})").format(
            aircraft_name, 
            part_name, 
            self.quantity,
            self.get_inventory_status_display()
        )

