from django.urls import path
from apps.parts.views import (
    PartTypeListView, PartView, PartDetailView, InventoryListView, InventorySummaryView
)

app_name = 'parts'

urlpatterns = [
    path('types/', PartTypeListView.as_view(), name='part-type-list'),
    path('', PartView.as_view(), name='part-list-create'),
    path('<int:part_id>/', PartDetailView.as_view(), name='part-detail'),
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('inventory/summary/', InventorySummaryView.as_view(), name='inventory-summary'),
]
