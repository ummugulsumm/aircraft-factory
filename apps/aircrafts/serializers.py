from rest_framework import serializers
from apps.aircrafts.models import Aircraft
from apps.parts.serializers import UsedPartSerializer
from apps.teams.enums import TeamTypes


class AircraftSerializer(serializers.ModelSerializer):

    aircraft_type_display = serializers.CharField(source='get_aircraft_type_display', read_only=True)
    assembled_by_name = serializers.SerializerMethodField()
    used_parts = UsedPartSerializer(many=True, read_only=True)
    
    class Meta:
        model = Aircraft
        fields = [
            'id', 'aircraft_type', 'aircraft_type_display', 'serial_number',
            'assembly_date', 'assembled_by_name', 'used_parts', 'created_at'
        ]
        read_only_fields = ['serial_number', 'assembly_date', 'created_at']
    
    def get_assembled_by_name(self, obj):
        if obj.assembled_by and obj.assembled_by.user:
            user = obj.assembled_by.user
            return f"{user.first_name} {user.last_name}" if user.first_name else user.username
        return None


class AircraftDetailSerializer(AircraftSerializer):
    used_parts = UsedPartSerializer(many=True, read_only=True)
    
    class Meta(AircraftSerializer.Meta):
        fields = AircraftSerializer.Meta.fields + ['used_parts']


class AircraftCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Aircraft
        fields = ['aircraft_type']
    
    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        if not hasattr(request.user, 'personnel'):
            raise serializers.ValidationError("User does not have associated personnel")
        
        personnel = request.user.personnel
        
        if personnel.team.type != TeamTypes.ASSEMBLY_TEAM:
            raise serializers.ValidationError("Only Assembly Team can create aircraft")
        
        return attrs
