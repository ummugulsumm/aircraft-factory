from django.db import models
from django.utils.translation import gettext_lazy as _

class TeamTypes(models.IntegerChoices):
    WING_TEAM = 1, _('Wing Team')
    BODY_TEAM = 2, _('Body Team')
    TAIL_TEAM = 3, _('Tail Team')
    AVIONICS_TEAM = 4, _('Avionics Team')
    ASSEMBLY_TEAM = 5, _('Assembly Team')