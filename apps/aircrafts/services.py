from django.db import transaction
from apps.aircrafts.models import Aircraft
from apps.parts.models import Part, UsedPart
from apps.teams.enums import TeamTypes
from apps.parts.enums import PartTypes, PartStatus
from apps.aircrafts.enums import AircraftTypes
from django.core.exceptions import ValidationError
from apps.parts.services import InventoryService


class AircraftService:
    
    @classmethod
    def check_required_parts(cls, aircraft_type):

        missing_parts = []
        
        for part_type in PartTypes:
            available_count = Part.objects.filter(
                part_type=part_type.value,
                aircraft_type=aircraft_type,
                status=PartStatus.AVAILABLE
            ).count()
            
            if available_count == 0:
                missing_parts.append({
                    'part_type': part_type.label,
                    'aircraft_type': AircraftTypes(aircraft_type).label
                })
        
        return missing_parts

    @classmethod
    def validate_part_availability(cls, part, aircraft_type):

        if part.status != PartStatus.AVAILABLE:
            raise ValidationError(f"Part {part.serial_number} is not available for use (Current status: {part.get_status_display()})")
        
        if hasattr(part, 'usage'):
            raise ValidationError(f"Part {part.serial_number} is already used in another aircraft")
            
        if part.aircraft_type != aircraft_type:
            raise ValidationError(
                f"Part {part.serial_number} ({part.get_aircraft_type_display()} {part.get_part_type_display()}) "
                f"cannot be used in {AircraftTypes(aircraft_type).label} aircraft"
            )

    @classmethod
    def assemble_aircraft(cls, aircraft_type, assembled_by):
        """Assemble an aircraft from available parts"""

        if assembled_by.team.type != TeamTypes.ASSEMBLY_TEAM:
            raise ValidationError("Only Assembly Team can assemble aircraft")
        
        missing_parts = cls.check_required_parts(aircraft_type)
        if missing_parts:
            missing_parts_str = ", ".join([f"{p['aircraft_type']} {p['part_type']}" for p in missing_parts])
            raise ValidationError(f"Missing required parts: {missing_parts_str}")
        
        with transaction.atomic():
            aircraft = Aircraft.objects.create(
                aircraft_type=aircraft_type,
                assembled_by=assembled_by
            )
            
            for part_type in PartTypes:
                part = Part.objects.filter(
                    part_type=part_type.value,
                    aircraft_type=aircraft_type,
                    status=PartStatus.AVAILABLE
                ).select_for_update().first()
                
                if part:
                    cls.validate_part_availability(part, aircraft_type)
                    
                    UsedPart.objects.create(
                        part=part,
                        aircraft=aircraft,
                        used_by=assembled_by
                    )
                    
                    part.status = PartStatus.IN_USE
                    part.save()
                    
                    InventoryService.decrease_inventory_for_part(part)
            
            return aircraft