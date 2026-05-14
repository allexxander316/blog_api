from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class TestAuthJWT(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data = {'username': 'testuser', 'password': 'secret'}
        cls.user = get_user_model().objects.create_user(username='testuser', password='secret')

    def setUp(self):
        self.client = APIClient()

    def test_get_token_from_valid_data(self):
        response = self.client.post(reverse('token_obtain_pair'), data=self.data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_token_from_invalid_data(self):
        invalid_data = self.data.copy()
        invalid_data['password'] = '1234'
        response = self.client.post(reverse('token_obtain_pair'), data=invalid_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)