from django.contrib import admin
from apps.aircrafts.models import Aircraft

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'aircraft_type', 'assembly_date', 'assembled_by')
    search_fields = ('serial_number',)
    list_filter = ('aircraft_type',)