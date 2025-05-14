from rest_framework import generics
from apps.teams.models import Team, Personnel
from apps.teams.serializers import TeamSerializer, TeamDetailSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Teams"])
class TeamListView(generics.ListAPIView):

    queryset = Team.objects.all()
    serializer_class = TeamSerializer


@extend_schema(tags=["Teams Detail"])
class TeamDetailView(generics.RetrieveAPIView):

    serializer_class = TeamDetailSerializer
    lookup_url_kwarg = 'team_id'
    
    def get_queryset(self):
        return Team.objects.all()
