from django.urls import path
from apps.aircrafts.views import (
    AircraftView, AircraftDetailView,
    CheckRequiredPartsView, AircraftTypeListView
)

app_name = 'aircrafts'

urlpatterns = [
    path('types/', AircraftTypeListView.as_view(), name='aircraft-type-list'),
    path('', AircraftView.as_view(), name='aircraft-list'),
    path('<int:pk>/', AircraftDetailView.as_view(), name='aircraft-detail'),
    path('check-parts/<int:aircraft_type>/', CheckRequiredPartsView.as_view(), name='check-required-parts'),
]