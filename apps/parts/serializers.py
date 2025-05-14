from rest_framework import serializers
from apps.parts.models import Part, UsedPart, Inventory
from apps.teams.serializers import TeamSerializer, PersonnelSerializer
from apps.aircrafts.enums import AircraftTypes
from apps.parts.enums import PartTypes
from apps.teams.models import Personnel
from django.utils.translation import gettext_lazy as _


class PartSerializer(serializers.ModelSerializer):

    part_type_display = serializers.SerializerMethodField()
    aircraft_type_display = serializers.CharField(source='get_aircraft_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    produced_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Part
        fields = [
            'id', 'part_type', 'part_type_display', 'aircraft_type', 'aircraft_type_display', 
            'serial_number', 'status', 'status_display', 'produced_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['serial_number', 'status', 'created_at', 'updated_at']
    
    def get_part_type_display(self, obj):
        return PartTypes(obj.part_type).label

    def get_produced_by(self, obj):
        if obj.produced_by and obj.produced_by.user:
            return {
                'id': obj.produced_by.id,
                'username': obj.produced_by.user.username,
                'full_name': obj.produced_by.user.get_full_name()
            }
        return None


class PartCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Part
        fields = ['part_type', 'aircraft_type']
    
    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError(_("Authentication credentials not provided"))
        
        try:
            personnel = Personnel.objects.get(user=request.user)
        except Personnel.DoesNotExist:
            raise serializers.ValidationError(_("User is not associated with any personnel"))
        
        if not personnel.team.is_responsible_for_part_type(data['part_type']):
            raise serializers.ValidationError(
                _("Your team is not responsible for producing this part type")
            )
        
        data['produced_by'] = personnel
        
        return data


class UsedPartSerializer(serializers.ModelSerializer):

    part = PartSerializer(read_only=True)
    aircraft_serial = serializers.CharField(source='aircraft.serial_number', read_only=True)
    used_by = PersonnelSerializer(read_only=True)
    
    class Meta:
        model = UsedPart
        fields = ['id', 'part', 'aircraft_serial', 'used_by', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class InventorySerializer(serializers.ModelSerializer):

    part_type_display = serializers.SerializerMethodField()
    aircraft_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['id', 'part_type', 'part_type_display', 'aircraft_type', 'aircraft_type_display', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_aircraft_type_display(self, obj):
        return AircraftTypes(obj.aircraft_type).label
    
    def get_part_type_display(self, obj):
        return PartTypes(obj.part_type).label