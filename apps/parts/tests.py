from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Part, UsedPart, Inventory
from apps.teams.models import Team, Personnel
from apps.aircrafts.models import Aircraft
from .enums import PartTypes, PartStatus, InventoryStatus
from apps.aircrafts.enums import AircraftTypes
from apps.teams.enums import TeamTypes

class PartModelTests(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.team = Team.objects.create(
            type=TeamTypes.WING_TEAM,
            description='Test Wing Team',
            responsible_part_type=PartTypes.WING
        )
        self.personnel = Personnel.objects.create(
            user=self.user,
            team=self.team
        )
        
        self.aircraft = Aircraft.objects.create(
            aircraft_type=AircraftTypes.TB2,
            assembled_by=self.personnel
        )

    def test_part_creation(self):

        """Test that a part can be created with required fields"""
        part = Part.objects.create(
            part_type=PartTypes.WING,
            aircraft_type=AircraftTypes.TB2,
            produced_by=self.personnel
        )
        self.assertIsNotNone(part)
        self.assertEqual(part.part_type, PartTypes.WING)
        self.assertEqual(part.aircraft_type, AircraftTypes.TB2)
        self.assertEqual(part.status, PartStatus.AVAILABLE)
        self.assertIsNotNone(part.serial_number)

    def test_used_part_creation(self):

        """Test creating a used part"""
        part = Part.objects.create(
            part_type=PartTypes.WING,
            aircraft_type=AircraftTypes.TB2,
            produced_by=self.personnel
        )
        used_part = UsedPart.objects.create(
            part=part,
            aircraft=self.aircraft,
            used_by=self.personnel
        )
        self.assertEqual(used_part.part, part)
        self.assertEqual(used_part.aircraft, self.aircraft)
        self.assertEqual(used_part.used_by, self.personnel)

    def test_inventory_creation(self):

        """Test inventory creation and status updates"""
        inventory = Inventory.objects.create(
            part_type=PartTypes.WING,
            aircraft_type=AircraftTypes.TB2,
            quantity=10
        )
        self.assertEqual(inventory.quantity, 10)
        self.assertEqual(inventory.inventory_status, InventoryStatus.ADEQUATE)

    def test_inventory_status_updates(self):

        """Test inventory status updates based on quantity"""
        inventory = Inventory.objects.create(
            part_type=PartTypes.WING,
            aircraft_type=AircraftTypes.TB2,
            quantity=10
        )
        
        inventory.quantity = 1
        inventory.save()
        self.assertEqual(inventory.inventory_status, InventoryStatus.CRITICAL)
        
        inventory.quantity = 4
        inventory.save()
        self.assertEqual(inventory.inventory_status, InventoryStatus.LOW)
        
        inventory.quantity = 0
        inventory.save()
        self.assertEqual(inventory.inventory_status, InventoryStatus.OUT_OF_STOCK)

class PartViewTests(APITestCase):
    def setUp(self):

        self.wing_team_user = User.objects.create_user(
            username='wing_user',
            email='wing@example.com',
            password='testpass123'
        )
        self.body_team_user = User.objects.create_user(
            username='body_user',
            email='body@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        self.wing_team = Team.objects.create(
            type=TeamTypes.WING_TEAM,
            description='Wing Team',
            responsible_part_type=PartTypes.WING
        )
        self.body_team = Team.objects.create(
            type=TeamTypes.BODY_TEAM,
            description='Body Team',
            responsible_part_type=PartTypes.BODY
        )
        
        self.wing_personnel = Personnel.objects.create(
            user=self.wing_team_user,
            team=self.wing_team
        )
        self.body_personnel = Personnel.objects.create(
            user=self.body_team_user,
            team=self.body_team
        )
        
        self.wing_part = Part.objects.create(
            part_type=PartTypes.WING,
            aircraft_type=AircraftTypes.TB2,
            produced_by=self.wing_personnel
        )
        self.body_part = Part.objects.create(
            part_type=PartTypes.BODY,
            aircraft_type=AircraftTypes.TB2,
            produced_by=self.body_personnel
        )
        
        Inventory.objects.create(
            part_type=PartTypes.WING,
            aircraft_type=AircraftTypes.TB2,
            quantity=1
        )
        Inventory.objects.create(
            part_type=PartTypes.BODY,
            aircraft_type=AircraftTypes.TB2,
            quantity=1
        )
        
        self.client = APIClient()

    def test_list_parts_with_wing_team(self):

        """Test listing parts with wing team user"""
        self.client.force_authenticate(user=self.wing_team_user)
        response = self.client.get('/api/parts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['part_type'], PartTypes.WING)

    def test_list_parts_with_body_team(self):

        """Test listing parts with body team user"""
        self.client.force_authenticate(user=self.body_team_user)
        response = self.client.get('/api/parts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['part_type'], PartTypes.BODY)

    def test_list_parts_with_staff(self):

        """Test listing parts with staff user"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get('/api/parts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_part_with_wrong_team(self):

        """Test creating part with wrong team"""
        self.client.force_authenticate(user=self.wing_team_user)
        data = {
            'part_type': PartTypes.BODY,
            'aircraft_type': AircraftTypes.TB2,
            'produced_by': self.wing_personnel.id
        }
        response = self.client.post('/api/parts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_part_with_correct_team(self):

        """Test creating part with correct team"""
        self.client.force_authenticate(user=self.wing_team_user)
        data = {
            'part_type': PartTypes.WING,
            'aircraft_type': AircraftTypes.TB2,
            'produced_by': self.wing_personnel.id
        }
        response = self.client.post('/api/parts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_recycle_part_with_wrong_team(self):

        """Test recycling part with wrong team"""
        self.client.force_authenticate(user=self.wing_team_user)
        response = self.client.delete(f'/api/parts/{self.body_part.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_recycle_part_with_correct_team(self):

        """Test recycling part with correct team"""
        self.client.force_authenticate(user=self.wing_team_user)
        response = self.client.delete(f'/api/parts/{self.wing_part.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_inventory_list_with_team(self):

        """Test listing inventory with team user"""
        self.client.force_authenticate(user=self.wing_team_user)
        response = self.client.get('/api/parts/inventory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see wing parts in inventory
        for item in response.data:
            self.assertEqual(item['part_type'], PartTypes.WING)

    def test_inventory_summary_with_team(self):

        """Test getting inventory summary with team user"""
        self.client.force_authenticate(user=self.wing_team_user)
        response = self.client.get('/api/parts/inventory/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIsInstance(response.data, dict)
        
        for aircraft_type, parts in response.data.items():
            self.assertIsInstance(parts, dict)
            for part_name, part_data in parts.items():
                self.assertEqual(part_data['part_type'], PartTypes.WING)
                self.assertIn('quantity', part_data)
                self.assertIn('status', part_data)
                self.assertIn('status_display', part_data)
