from django.test import TestCase
from django.contrib.auth.models import User
from .models import Team, Personnel
from .enums import TeamTypes
from apps.parts.enums import PartTypes

class TeamModelTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            type=TeamTypes.WING_TEAM,
            description='Test Wing Team',
            responsible_part_type=PartTypes.WING
        )

    def test_team_creation(self):

        """Test that a team can be created with required fields"""
        self.assertIsNotNone(self.team)
        self.assertEqual(self.team.type, TeamTypes.WING_TEAM)
        self.assertEqual(self.team.responsible_part_type, PartTypes.WING)
        self.assertEqual(str(self.team), self.team.get_type_display())

    def test_team_part_type_responsibility(self):

        """Test team's part type responsibility check"""
        self.assertTrue(self.team.is_responsible_for_part_type(PartTypes.WING))
        self.assertFalse(self.team.is_responsible_for_part_type(PartTypes.BODY))

class PersonnelModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.team = Team.objects.create(
            type=TeamTypes.WING_TEAM,
            description='Test Wing Team'
        )
        
        self.personnel = Personnel.objects.create(
            user=self.user,
            team=self.team
        )

    def test_personnel_creation(self):

        """Test that personnel can be created with required fields"""
        self.assertIsNotNone(self.personnel)
        self.assertEqual(self.personnel.user, self.user)
        self.assertEqual(self.personnel.team, self.team)


