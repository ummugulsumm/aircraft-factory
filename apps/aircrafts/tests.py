from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Aircraft
from apps.teams.models import Team, Personnel
from .enums import AircraftTypes
from apps.teams.enums import TeamTypes
from apps.parts.models import Part, Inventory
from apps.parts.enums import PartTypes

class AircraftModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.team = Team.objects.create(
            type=TeamTypes.ASSEMBLY_TEAM,
            description='Test Assembly Team'
        )
        
        self.personnel = Personnel.objects.create(
            user=self.user,
            team=self.team
        )

    def test_aircraft_creation(self):
        """Test that an aircraft can be created with required fields"""
        aircraft = Aircraft.objects.create(
            aircraft_type=AircraftTypes.TB2,
            assembled_by=self.personnel
        )
        self.assertIsNotNone(aircraft)
        self.assertEqual(aircraft.aircraft_type, AircraftTypes.TB2)
        self.assertEqual(aircraft.assembled_by, self.personnel)
        self.assertIsNotNone(aircraft.serial_number)
        self.assertTrue(aircraft.serial_number.startswith('AC-TB2'))


    def test_different_aircraft_types(self):
        """Test creating different types of aircraft"""

        tb2 = Aircraft.objects.create(
            aircraft_type=AircraftTypes.TB2,
            assembled_by=self.personnel
        )
        self.assertEqual(tb2.aircraft_type, AircraftTypes.TB2)
        self.assertTrue(tb2.serial_number.startswith('AC-TB2'))

        tb3 = Aircraft.objects.create(
            aircraft_type=AircraftTypes.TB3,
            assembled_by=self.personnel
        )
        self.assertEqual(tb3.aircraft_type, AircraftTypes.TB3)
        self.assertTrue(tb3.serial_number.startswith('AC-TB3'))

        akinci = Aircraft.objects.create(
            aircraft_type=AircraftTypes.AKINCI,
            assembled_by=self.personnel
        )
        self.assertEqual(akinci.aircraft_type, AircraftTypes.AKINCI)
        self.assertTrue(akinci.serial_number.startswith('AC-AKINCI'))

        kizilelma = Aircraft.objects.create(
            aircraft_type=AircraftTypes.KIZILELMA,
            assembled_by=self.personnel
        )
        self.assertEqual(kizilelma.aircraft_type, AircraftTypes.KIZILELMA)
        self.assertTrue(kizilelma.serial_number.startswith('AC-KIZILELMA'))

class AircraftViewTests(APITestCase):
    def setUp(self):

        self.assembly_user = User.objects.create_user(
            username='assembly_user',
            email='assembly@example.com',
            password='testpass123'
        )
        self.non_assembly_user = User.objects.create_user(
            username='non_assembly_user',
            email='non_assembly@example.com',
            password='testpass123'
        )
        
        self.assembly_team = Team.objects.create(
            type=TeamTypes.ASSEMBLY_TEAM,
            description='Assembly Team'
        )
        self.wing_team = Team.objects.create(
            type=TeamTypes.WING_TEAM,
            description='Wing Team'
        )
        
        self.assembly_personnel = Personnel.objects.create(
            user=self.assembly_user,
            team=self.assembly_team
        )
        self.non_assembly_personnel = Personnel.objects.create(
            user=self.non_assembly_user,
            team=self.wing_team
        )
        
        self.aircraft = Aircraft.objects.create(
            aircraft_type=AircraftTypes.TB2,
            assembled_by=self.assembly_personnel
        )
        
        self.client = APIClient()

    def test_list_aircraft_with_assembly_team(self):
       
        """Test listing aircraft with assembly team permission"""
        self.client.force_authenticate(user=self.assembly_user)
        response = self.client.get('/api/aircrafts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_aircraft_without_assembly_team(self):
        
        """Test listing aircraft without assembly team permission"""
        self.client.force_authenticate(user=self.non_assembly_user)
        response = self.client.get('/api/aircrafts/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_aircraft_with_assembly_team(self):
        
        """Test creating aircraft with assembly team permission"""
        self.client.force_authenticate(user=self.assembly_user)
        
        for part_type in [PartTypes.WING, PartTypes.BODY, PartTypes.TAIL, PartTypes.AVIONICS]:
            part = Part.objects.create(
                part_type=part_type,
                aircraft_type=AircraftTypes.TB2,
                produced_by=self.assembly_personnel
            )
            Inventory.objects.create(
                part_type=part_type,
                aircraft_type=AircraftTypes.TB2,
                quantity=1
            )
        
        data = {'aircraft_type': AircraftTypes.TB2}
        response = self.client.post('/api/aircrafts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Aircraft.objects.count(), 2)

    def test_create_aircraft_without_assembly_team(self):
        
        """Test creating aircraft without assembly team permission"""
        self.client.force_authenticate(user=self.non_assembly_user)
        data = {'aircraft_type': AircraftTypes.TB2}
        response = self.client.post('/api/aircrafts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Aircraft.objects.count(), 1)

    def test_create_aircraft_without_required_parts(self):
        
        """Test creating aircraft without required parts"""
        self.client.force_authenticate(user=self.assembly_user)
        data = {'aircraft_type': AircraftTypes.TB2}
        response = self.client.post('/api/aircrafts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Aircraft.objects.count(), 1)
