from rest_framework import permissions
from apps.teams.models import Team
from apps.teams.enums import TeamTypes

class TeamBasedPermission(permissions.BasePermission):
    
    def __init__(self, team_type):
        self.team_type = team_type
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'personnel') and
            request.user.personnel.team.type == self.team_type
        )

class IsAssemblyTeam(TeamBasedPermission):

    def __init__(self):
        super().__init__(TeamTypes.ASSEMBLY_TEAM)