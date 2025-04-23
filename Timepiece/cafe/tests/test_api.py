from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from cafe.models import Category, MenuItem, Order, Review
from decimal import Decimal
import json

class CategoryAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/categories/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category1 = Category.objects.create(name="Coffee", description="Coffee drinks")
        self.category2 = Category.objects.create(name="Food", description="Food items")
    
    def test_get_all_categories(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_single_category(self):
        response = self.client.get(f"{self.url}{self.category1.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Coffee")
        self.assertEqual(response.data['description'], "Coffee drinks")
    
    def test_create_category(self):
        data = {
            'name': 'Desserts',
            'description': 'Sweet treats'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Category.objects.get(name='Desserts').description, 'Sweet treats')

class MenuItemAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/menu-items/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name="Coffee")
        self.menu_item = MenuItem.objects.create(
            name="Espresso",
            description="Strong coffee",
            price=Decimal('2.50'),
            category=self.category,
            is_available=True
        )
    
    def test_get_all_menu_items(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_single_menu_item(self):
        response = self.client.get(f"{self.url}{self.menu_item.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Espresso")
        self.assertEqual(response.data['price'], '2.50')
    
    def test_create_menu_item(self):
        data = {
            'name': 'Latte',
            'description': 'Coffee with milk',
            'price': '3.50',
            'category_id': self.category.id,
            'is_available': True
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 2)
        self.assertEqual(MenuItem.objects.get(name='Latte').price, Decimal('3.50'))
    
    def test_filter_menu_items_by_category(self):
        # Create a second category and menu items
        food_category = Category.objects.create(name="Food")
        MenuItem.objects.create(
            name="Sandwich",
            description="Ham and cheese",
            price=Decimal('5.50'),
            category=food_category,
            is_available=True
        )
        
        # Filter by coffee category
        response = self.client.get(f"{self.url}?category={self.category.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Espresso")

class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/orders/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name="Coffee")
        self.menu_item = MenuItem.objects.create(
            name="Espresso",
            description="Strong coffee",
            price=Decimal('2.50'),
            category=self.category
        )
        
        # Create an order
        self.order = Order.objects.create(
            customer=self.user,
            status="PENDING",
            total_amount=Decimal('5.00')
        )
    
    def test_get_user_orders(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_order(self):
        data = {
            'status': 'PENDING',
            'notes': 'Test order',
            'order_items': [
                {
                    'menu_item_id': self.menu_item.id,
                    'quantity': 2
                }
            ]
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        
        # Check the order has the correct total amount
        new_order = Order.objects.get(id=response.data['id'])
        self.assertEqual(new_order.total_amount, Decimal('5.00'))  # 2 * 2.50

class ReviewAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/reviews/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name="Coffee")
        self.menu_item = MenuItem.objects.create(
            name="Espresso",
            description="Strong coffee",
            price=Decimal('2.50'),
            category=self.category
        )
    
    def test_create_review(self):
        data = {
            'menu_item_id': self.menu_item.id,
            'rating': 5,
            'comment': 'Excellent coffee!'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        
        review = Review.objects.first()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent coffee!')
        self.assertEqual(review.customer, self.user)
        self.assertEqual(review.menu_item, self.menu_item)

class AuthenticationAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.token_url = '/api-token-auth/'
        self.menu_items_url = '/api/menu-items/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
    
    def test_get_auth_token(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.token_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
    
    def test_authenticated_request(self):
        # First get the auth token
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.token_url, data, format='json')
        token = response.data['token']
        
        # Use the token for authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get(self.menu_items_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthenticated_request_to_protected_endpoint(self):
        # No authentication
        orders_url = '/api/orders/'
        response = self.client.get(orders_url)
        
        # Should be denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 