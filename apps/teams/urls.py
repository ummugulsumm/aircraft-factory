from django.urls import path
from apps.teams.views import TeamListView, TeamDetailView

urlpatterns = [
    path('', TeamListView.as_view(), name='team-list'),
    path('<int:team_id>', TeamDetailView.as_view(), name='team-detail'),
]