from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from apps.teams.models import Personnel, Team
from apps.teams.serializers import TeamSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    team_id = serializers.IntegerField(write_only=True, required=True)
    team = TeamSerializer(source='personnel.team', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'email', 'first_name', 'last_name', 'team_id', 'team']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        try:
            Team.objects.get(id=attrs['team_id'])
        except Team.DoesNotExist:
            raise serializers.ValidationError({"team_id": "Selected team not found."})
            
        return attrs
        
    def create(self, validated_data):
        team_id = validated_data.pop('team_id')
        validated_data.pop('password2')
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        Personnel.objects.create(
            user=user,
            team_id=team_id
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, required=True, write_only=True)


    