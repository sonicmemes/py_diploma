import os
import django
from backend.models import User, ConfirmEmailToken, Category, Shop
from django.test.runner import DiscoverRunner
from unittest import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from backend import models
from backend.views import RegisterAccount

from backend.serializers import ShopSerializer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')
django.setup()


class TestRegisterAccount(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post(self):
        # Create a sample user data
        user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123!',
            'company': 'Example Inc.',
            'position': 'Software Engineer'
        }

        # Send a POST request to the register endpoint
        url = reverse('backend:user-register')
        response = self.client.post(url, user_data, format='json')

        # Print the response content
        print(response.content)

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

        # Verify the response content
        self.assertEqual(response.json(), {'Status': True})

        # Verify that the user is created in the database
        self.assertTrue(models.User.objects.filter(email='john@example.com').exists())


class TestConfirmAccount(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.token = ConfirmEmailToken.objects.create(user=self.user, key='some_token')

        self.client.force_authenticate(user=self.user)

    def test_post(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Print out the token key
        print("Token key:", self.token.key)

        # Send a POST request to the confirm account endpoint
        url = reverse('backend:user-register-confirm')
        data = {'email': self.user.email, 'token': self.token.key}
        response = self.client.post(url, data, format='json')

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

        # Verify that the user is active
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

        # Additional assertions
        self.assertEqual(response.json(), {'Status': True})  # Verify the response content
        # Refresh the self.user object from the database
        self.user.refresh_from_db()

        # Verify that the confirmation token is deleted
        with self.assertRaises(ConfirmEmailToken.DoesNotExist):
            self.token.refresh_from_db()


class TestAccountDetails(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get(self):
        # Send a GET request to the account details endpoint
        url = reverse('backend:user-details')
        response = self.client.get(url)

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

        # Verify that the response contains the user's email
        self.assertEqual(response.json()['email'], self.user.email)

    def test_post(self):
        # Send a POST request to the account details endpoint with invalid data
        url = reverse('backend:user-details')
        data = {'email': 'invalid_email'}
        response = self.client.post(url, data, format='json')

        # Verify the response status code
        self.assertEqual(response.status_code, 400)

        # Verify that the response contains an error message
        self.assertIn('Errors', response.json())
        self.assertIn('email', response.json()['Errors'])

        # Send a POST request to the account details endpoint with valid data
        data = {'email': 'new_email@example.com'}
        response = self.client.post(url, data, format='json')

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

        # Verify that the user's email has been updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new_email@example.com')


class TestLoginAccount(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client = APIClient()

    def test_post(self):
        # Send a POST request to the login endpoint with valid data
        url = reverse('backend:user-login')
        data = {'email': 'test@example.com', 'password': 'password'}
        response = self.client.post(url, data, format='json')

        # Verify the response status code
        self.assertEqual(response.status_code, 200)


class TestCategoryView(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.client = APIClient()

    def test_get(self):
        # Send a GET request to the category endpoint
        url = reverse('backend:categories')
        response = self.client.get(url, format='json')

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

        # Verify that the response contains a list of categories
        self.assertIsInstance(response.json(), list)

        # Verify that the category is in the list
        self.assertIn(self.category.name, [category['name'] for category in response.json()])


class TestShopView(TestCase):
    def setUp(self):
        self.shop1 = Shop.objects.create(name='Test Shop 1', state=True)
        self.shop1.state = True
        self.shop1.save()
        print("Shop1 created:", self.shop1)
        self.shop2 = Shop.objects.create(name='Test Shop 2', state=False)
        self.shop2.state = False
        self.shop2.save()
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@example.com')
        self.client.force_authenticate(user=self.user)

    def test_get(self):
        # Retrieve a shop from the database
        shop = Shop.objects.get(name='Test Shop 1')
        serializer = ShopSerializer(shop)
        print("Serialized shop:", serializer.data)
        # Retrieve all shops from the database
        shops = Shop.objects.all()
        print("Shops:", shops)
        # Retrieve the shop with state=True from the database
        shop = Shop.objects.get(name='Test Shop 1', state=True)
        self.assertIsNotNone(shop)  # Verify that the shop exists
        # Send a GET request to the shop endpoint
        url = reverse('backend:shops')
        response = self.client.get(url, format='json')

        # Print the response status code and content
        print("Response status code:", response.status_code)
        print("Response content:", response.content)

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

        # Verify that the response contains a list of shops
        self.assertIsInstance(response.json(), list)

        # Print the response data to the console
        print(f"responce: {response.json()}")

        # Verify that only shops with state=True are in the list
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['name'], self.shop1.name)


class TestProductInfoView(TestCase):
    def test_get(self):
        self.fail()


class TestBasketView(TestCase):
    def test_get(self):
        self.fail()

    def test_post(self):
        self.fail()

    def test_delete(self):
        self.fail()

    def test_put(self):
        self.fail()


class TestPartnerUpdate(TestCase):
    def test_post(self):
        self.fail()


class TestPartnerState(TestCase):
    def test_get(self):
        self.fail()

    def test_post(self):
        self.fail()


class TestPartnerOrders(TestCase):
    def test_get(self):
        self.fail()


class TestContactView(TestCase):
    def test_get(self):
        self.fail()

    def test_post(self):
        self.fail()

    def test_delete(self):
        self.fail()

    def test_put(self):
        self.fail()


class TestOrderView(TestCase):
    def test_get(self):
        self.fail()

    def test_post(self):
        self.fail()
