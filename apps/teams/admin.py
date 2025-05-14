from django.contrib import admin
from apps.teams.models import Personnel, Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('type', 'description')


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('user', 'team')
