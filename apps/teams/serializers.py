from rest_framework import serializers
from django.contrib.auth.models import User
from apps.teams.models import Team, Personnel


class TeamSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'type', 'type_display', 'description']


class UserBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class PersonnelSerializer(serializers.ModelSerializer):
    
    user = UserBasicSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    
    class Meta:
        model = Personnel
        fields = ['id', 'user', 'team']


class TeamDetailSerializer(serializers.ModelSerializer):
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    members = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'type', 'type_display', 'description', 'members']
    
    def get_members(self, obj):
        
        personnel = Personnel.objects.filter(team=obj).select_related('user')
        users = [item.user for item in personnel]
        return UserBasicSerializer(users, many=True).data

