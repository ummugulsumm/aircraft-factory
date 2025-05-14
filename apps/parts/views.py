from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.parts.models import Part, Inventory
from apps.parts.serializers import (
    PartSerializer, PartCreateSerializer, InventorySerializer
)
from apps.parts.services import PartService, InventoryService
from common.permissions import IsAssemblyTeam
from drf_spectacular.utils import extend_schema
from apps.parts.enums import PartTypes
from rest_framework.exceptions import PermissionDenied, NotFound
from django.core.exceptions import ValidationError


@extend_schema(tags=["Part Types"])
class PartTypeListView(APIView):
    
    def get(self, request):
        types = [{'id': t.value, 'name': t.label} for t in PartTypes]
        return Response(types)


@extend_schema(tags=["Parts"])
class PartView(generics.ListCreateAPIView):

    queryset = Part.objects.all().select_related('produced_by__user')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PartCreateSerializer
        return PartSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        part_type = self.request.query_params.get('part_type')
        aircraft_type = self.request.query_params.get('aircraft_type')
        status = self.request.query_params.get('status')
        
        if part_type:
            queryset = queryset.filter(part_type=part_type)
        
        if aircraft_type:
            queryset = queryset.filter(aircraft_type=aircraft_type)
        
        if status is not None:
            try:
                status = int(status)
                queryset = queryset.filter(status=status)
            except ValueError:
                queryset = queryset.none()
        
        if not self.request.user.is_staff:
            if hasattr(self.request.user, 'personnel'):
                team = self.request.user.personnel.team
                queryset = queryset.filter(part_type=team.responsible_part_type)
            else:
                queryset = queryset.none()
        
        return queryset

    def perform_create(self, serializer):

        validated_data = serializer.validated_data
        part = PartService.create_part(
            part_type=validated_data['part_type'],
            aircraft_type=validated_data['aircraft_type'],
            produced_by=validated_data['produced_by']
        )
        serializer.instance = part


@extend_schema(tags=["Part Details"])
class PartDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = PartSerializer
    lookup_url_kwarg = 'part_id'
    
    def get_queryset(self):
        queryset = Part.objects.all().select_related('produced_by__user')
        
        if not self.request.user.is_staff:
            if hasattr(self.request.user, 'personnel'):
                team = self.request.user.personnel.team
                queryset = queryset.filter(part_type=team.responsible_part_type)
            else:
                queryset = queryset.none()
        
        return queryset
    
    def perform_destroy(self, instance):

        if not hasattr(self.request.user, 'personnel'):
            raise PermissionDenied("User does not have associated personnel")
        
        result = PartService.recycle_part(instance.id, self.request.user.personnel)
        
        if not result:
            raise NotFound("Part not found or cannot be recycled")


@extend_schema(tags=["Inventory"])
class InventoryListView(generics.ListAPIView):

    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()

        part_type = self.request.query_params.get('part_type')
        aircraft_type = self.request.query_params.get('aircraft_type')
        
        if part_type:
            queryset = queryset.filter(part_type=part_type)
        
        if aircraft_type:
            queryset = queryset.filter(aircraft_type=aircraft_type)
        
        if not self.request.user.is_staff:
            if hasattr(self.request.user, 'personnel'):
                team = self.request.user.personnel.team
                queryset = queryset.filter(part_type=team.responsible_part_type)
            else:
                queryset = queryset.none()
        
        return queryset


@extend_schema(tags=["Inventory"])
class InventorySummaryView(APIView):
    """Get inventory summary by aircraft type"""

    def get(self, request):
        summary = {}
        
        if request.user.is_staff:
            summary = InventoryService.get_inventory_summary()
        else:
            if hasattr(request.user, 'personnel'):
                team = request.user.personnel.team
                summary = InventoryService.get_inventory_summary(team.responsible_part_type)
        
        return Response(summary)

