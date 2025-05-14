from django.db import models
from django.utils.translation import gettext_lazy as _


class PartTypes(models.IntegerChoices):
    WING = 1, _('Wing')
    BODY = 2, _('Body')
    TAIL = 3, _('Tail')
    AVIONICS = 4, _('Avionics')


class PartStatus(models.IntegerChoices):
    AVAILABLE = 1, _("Available")           
    IN_USE = 2, _("In Use")                 
    IN_RECYCLING = 3, _("In Recycling")     


class InventoryStatus(models.IntegerChoices):
    ADEQUATE = 0, _('Adequate')
    LOW = 1, _('Low Stock')
    CRITICAL = 2, _('Critical Stock')
    OUT_OF_STOCK = 3, _('Out of Stock')