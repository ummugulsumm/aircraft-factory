from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer
from apps.teams.models import Personnel
from django.utils.translation import gettext_lazy as _  
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Register"])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

@extend_schema(tags=["Login"])
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return Response({'error': _('Invalid username or password.')}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            Personnel.objects.select_related('team').get(user=user)
        except Personnel.DoesNotExist:
            return Response({'error': _('Personnel could not be found.')}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return Response(data, status=status.HTTP_200_OK)

@extend_schema(tags=["Profile"])
class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
