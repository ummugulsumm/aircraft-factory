from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.aircrafts.models import Aircraft
from apps.aircrafts.serializers import (
    AircraftSerializer, AircraftDetailSerializer, AircraftCreateSerializer
)
from apps.aircrafts.services import AircraftService
from common.permissions import IsAssemblyTeam
from drf_spectacular.utils import extend_schema
from apps.aircrafts.enums import AircraftTypes
from rest_framework.exceptions import ValidationError


@extend_schema(tags=["Aircraft Types"])
class AircraftTypeListView(APIView):
    
    def get(self, request):
        types = [{'id': t.value, 'name': t.label} for t in AircraftTypes]
        return Response(types)


@extend_schema(tags=["Aircraft"])
class AircraftView(generics.ListCreateAPIView):
  
    queryset = Aircraft.objects.all().select_related('assembled_by__user')
    permission_classes = [IsAssemblyTeam]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AircraftCreateSerializer
        return AircraftSerializer
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        aircraft_type = self.request.query_params.get('aircraft_type')
        if aircraft_type:
            queryset = queryset.filter(aircraft_type=aircraft_type)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            aircraft_type = serializer.validated_data['aircraft_type']
            
            missing_parts = AircraftService.check_required_parts(aircraft_type)
            if missing_parts:
                missing_parts_str = ", ".join([f"{p['aircraft_type']} {p['part_type']}" for p in missing_parts])
                return Response(
                    {"detail": f"Missing required parts: {missing_parts_str}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            aircraft = AircraftService.assemble_aircraft(
                aircraft_type=aircraft_type,
                assembled_by=request.user.personnel
            )
            
            result_serializer = AircraftDetailSerializer(aircraft)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Aircraft Details"])
class AircraftDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = AircraftSerializer
    lookup_url_kwarg = 'pk'
    
    def get_queryset(self):
        return Aircraft.objects.all().select_related(
            'assembled_by__user',
            'assembled_by__team'
        )


@extend_schema(tags=["Aircraft Parts"])
class CheckRequiredPartsView(APIView):
    
    def get(self, request, aircraft_type):
        try:
            if aircraft_type not in [t.value for t in AircraftTypes]:
                raise ValidationError("Invalid aircraft type")
            
            availability = AircraftService.check_required_parts_availability(aircraft_type)
            return Response(availability)
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)