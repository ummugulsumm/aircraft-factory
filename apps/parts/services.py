from django.db import transaction
from apps.parts.models import Part, Inventory
from apps.parts.enums import PartStatus, PartTypes, InventoryStatus
from apps.aircrafts.enums import AircraftTypes
from django.core.exceptions import ValidationError

class PartService:
    
    @classmethod
    def create_part(cls, part_type, aircraft_type, produced_by):

        if not produced_by.team.is_responsible_for_part_type(part_type):
            raise ValidationError("Your team is not responsible for producing this part type")
            
        with transaction.atomic():
            part = Part.objects.create(
                part_type=part_type,
                aircraft_type=aircraft_type,
                produced_by=produced_by
            )
            
            inventory, created = Inventory.objects.get_or_create(
                part_type=part_type,
                aircraft_type=aircraft_type,
                defaults={'quantity': 0}
            )
            inventory.quantity += 1
            inventory.save()
            
            return part
    
    @classmethod
    def get_available_parts(cls, part_type, aircraft_type):
        return Part.objects.filter(
            part_type=part_type,
            aircraft_type=aircraft_type,
            status=PartStatus.AVAILABLE
        )
    
    @classmethod
    def recycle_part(cls, part_id, personnel):

        try:
            part = Part.objects.get(id=part_id, status=PartStatus.AVAILABLE)

            if not personnel.team.is_responsible_for_part_type(part.part_type):
                raise ValidationError("Your team is not responsible for recycling this part type")
            
            with transaction.atomic():
                InventoryService.decrease_inventory_for_part(part)
                
                part.status = PartStatus.IN_RECYCLING
                part.save()
                return True
        except Part.DoesNotExist:
            return False
        except Inventory.DoesNotExist:
            return False



class InventoryService:

    @classmethod
    def ensure_inventory_records(cls):
        from apps.parts.enums import PartTypes
        from apps.aircrafts.enums import AircraftTypes
        from apps.parts.models import Inventory

        for aircraft_type in AircraftTypes:
            for part_type in PartTypes:
                Inventory.objects.get_or_create(
                    aircraft_type=aircraft_type.value,
                    part_type=part_type.value,
                    defaults={
                        'quantity': 0,
                        'threshold_low': 5,
                        'threshold_critical': 2
                    }
                )

    @classmethod
    def get_inventory_summary(cls, part_type=None):

        cls.ensure_inventory_records()
        
        inventory_items = Inventory.objects.all()
        
        if part_type is not None:
            inventory_items = inventory_items.filter(part_type=part_type)
            
        summary = {}
        
        for item in inventory_items:
            aircraft_name = str(AircraftTypes(item.aircraft_type).label)
            part_name = str(PartTypes(item.part_type).label)
            
            if aircraft_name not in summary:
                summary[aircraft_name] = {}
            
            summary[aircraft_name][part_name] = {
                'quantity': item.quantity,
                'status': item.inventory_status,
                'status_display': str(item.get_inventory_status_display()),
                'part_type': item.part_type,
                'aircraft_type': item.aircraft_type
            }
        
        return summary

    @classmethod
    def get_low_stock_items(cls):

        return Inventory.objects.filter(
            status__gt=Inventory.InventoryStatus.ADEQUATE
        ).select_related('part_type').order_by('status', 'part_type__type')

    @classmethod
    def check_assembly_requirements(cls, aircraft_type):

        inventories = Inventory.objects.filter(
            aircraft_type=aircraft_type
        ).select_related('part_type')
        
        missing_parts = []
        low_stock_parts = []
        
        for inventory in inventories:
            if inventory.status == Inventory.InventoryStatus.OUT_OF_STOCK:
                missing_parts.append(inventory.part_type.get_type_display())
            elif inventory.status > Inventory.InventoryStatus.ADEQUATE:
                low_stock_parts.append({
                    'part_type': inventory.part_type.get_type_display(),
                    'quantity': inventory.quantity,
                    'status': inventory.get_status_display()
                })
        
        return {
            'can_assemble': len(missing_parts) == 0,
            'missing_parts': missing_parts,
            'low_stock_warning': low_stock_parts
        }

    @classmethod
    def update_quantity(cls, inventory_id, change_amount):

        with transaction.atomic():
            inventory = Inventory.objects.select_for_update().get(id=inventory_id)
            
            new_quantity = inventory.quantity + change_amount
            if new_quantity < 0:
                raise ValidationError("Cannot reduce inventory below zero")
            
            inventory.quantity = new_quantity
            inventory.save()

    @classmethod
    def decrease_inventory_for_part(cls, part):

        with transaction.atomic():
            inventory = Inventory.objects.select_for_update().get(
                part_type=part.part_type,
                aircraft_type=part.aircraft_type
            )
            if inventory.quantity > 0:
                inventory.quantity -= 1
                inventory.save()
            else:
                raise ValidationError(f"No inventory available for part type {part.get_part_type_display()}")