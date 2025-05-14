from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from common.mixins import TimestampMixin
from apps.teams.enums import TeamTypes
from apps.parts.enums import PartTypes
from django.contrib.postgres.fields import ArrayField

class Team(TimestampMixin):

    type = models.PositiveSmallIntegerField(_("Team Type"), choices=TeamTypes.choices, unique=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    responsible_part_type = models.PositiveSmallIntegerField(_("Responsible Part Type"), choices=PartTypes.choices, null=True, blank=True)

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")

    def __str__(self):
        return self.get_type_display()

    def is_responsible_for_part_type(self, part_type):
        return part_type == self.responsible_part_type


class Personnel(TimestampMixin):

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='personnel',
        verbose_name=_("User")
    )
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE, 
        related_name='personnel',
        verbose_name=_("Team")
    )

    class Meta:
        verbose_name = _("Personnel")
        verbose_name_plural = _("Personnel")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.team}"