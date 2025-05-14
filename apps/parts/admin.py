from django.contrib import admin
from apps.parts.models import Part, UsedPart, Inventory


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'get_part_type_display', 'get_aircraft_type_display', 'status', 'produced_by')
    search_fields = ('serial_number',)
    list_filter = ('part_type', 'aircraft_type', 'status')

    def get_part_type_display(self, obj):
        return obj.get_part_type_display()
    get_part_type_display.short_description = 'Part Type'

    def get_aircraft_type_display(self, obj):
        return obj.get_aircraft_type_display()
    get_aircraft_type_display.short_description = 'Aircraft Type'


@admin.register(UsedPart)
class UsedPartAdmin(admin.ModelAdmin):
    list_display = ('part', 'aircraft', 'used_by')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('get_part_type_display', 'get_aircraft_type_display', 'quantity', 'inventory_status')
    list_filter = ('part_type', 'aircraft_type', 'inventory_status')

    def get_part_type_display(self, obj):
        return obj.get_part_type_display()
    get_part_type_display.short_description = 'Part Type'

    def get_aircraft_type_display(self, obj):
        return obj.get_aircraft_type_display()
    get_aircraft_type_display.short_description = 'Aircraft Type'
