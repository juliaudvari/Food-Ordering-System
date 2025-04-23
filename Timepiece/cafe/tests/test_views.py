from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from cafe.models import Category, MenuItem, CustomerProfile, Order
from decimal import Decimal

class HomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('cafe:home')
        
        # Create test data
        self.category = Category.objects.create(name="Coffee")
        for i in range(6):
            MenuItem.objects.create(
                name=f"Test Item {i}",
                description=f"Description {i}",
                price=Decimal('2.50'),
                category=self.category,
                is_available=True
            )
    
    def test_home_view_GET(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cafe/home.html')
        self.assertContains(response, 'TimeKeeper Cafe')
        
        # Check if featured items are in the context
        self.assertTrue('featured_items' in response.context)
        self.assertTrue(len(response.context['featured_items']) > 0)

class MenuViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('cafe:menu')
        
        # Create test data
        self.coffee_category = Category.objects.create(name="Coffee")
        self.food_category = Category.objects.create(name="Food")
        
        # Create coffee items
        for i in range(3):
            MenuItem.objects.create(
                name=f"Coffee {i}",
                description=f"Coffee description {i}",
                price=Decimal('2.50'),
                category=self.coffee_category,
                is_available=True
            )
        
        # Create food items
        for i in range(2):
            MenuItem.objects.create(
                name=f"Food {i}",
                description=f"Food description {i}",
                price=Decimal('5.50'),
                category=self.food_category,
                is_available=True
            )
    
    def test_menu_view_GET(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cafe/menu.html')
        
        # Check context data
        self.assertTrue('menu_items' in response.context)
        self.assertTrue('categories' in response.context)
        self.assertEqual(len(response.context['categories']), 2)
        
        # Check all items are shown
        self.assertEqual(len(response.context['menu_items']), 5)
    
    def test_menu_view_with_category_filter(self):
        url = reverse('cafe:menu_category', args=[self.coffee_category.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Check only coffee items are shown
        self.assertEqual(len(response.context['menu_items']), 3)
        for item in response.context['menu_items']:
            self.assertEqual(item.category, self.coffee_category)

class MenuItemDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(name="Coffee")
        self.menu_item = MenuItem.objects.create(
            name="Espresso",
            description="Strong coffee",
            price=Decimal('2.50'),
            category=self.category,
            is_available=True
        )
        
        # Create related items
        for i in range(3):
            MenuItem.objects.create(
                name=f"Related Coffee {i}",
                description=f"Related description {i}",
                price=Decimal('3.50'),
                category=self.category,
                is_available=True
            )
        
        self.url = reverse('cafe:menu_item_detail', args=[self.menu_item.id])
    
    def test_menu_item_detail_view_GET(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cafe/menu_item_detail.html')
        
        # Check context data
        self.assertTrue('menu_item' in response.context)
        self.assertEqual(response.context['menu_item'], self.menu_item)
        
        # Check related items
        self.assertTrue('related_items' in response.context)
        self.assertTrue(len(response.context['related_items']) > 0)
        
        # Check content
        self.assertContains(response, self.menu_item.name)
        self.assertContains(response, self.menu_item.description)
        self.assertContains(response, str(self.menu_item.price))

class UserAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('two_factor:login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
    
    def test_login_page_GET(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'two_factor/core/login.html')
    
    def test_login_with_valid_credentials(self):
        response = self.client.post(self.login_url, {
            'auth-username': 'testuser',
            'auth-password': 'testpassword123',
            'login_view-current_step': 'auth'
        }, follow=True)
        
        # Should redirect to the next step in two-factor setup or to home if not set up
        self.assertEqual(response.status_code, 200)
        
        # Check if user is authenticated
        user = response.context['user']
        self.assertTrue(user.is_authenticated)

class ProtectedViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create an order for the user
        self.order = Order.objects.create(
            customer=self.user,
            status='PENDING',
            total_amount=Decimal('10.00')
        )
    
    def test_profile_view_requires_login(self):
        # Assuming you have a profile view
        profile_url = '/profile/'
        response = self.client.get(profile_url)
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login'))
    
    def test_profile_view_with_login(self):
        # Login the user
        self.client.login(username='testuser', password='testpassword123')
        
        # Assuming you have a profile view
        profile_url = '/profile/'
        response = self.client.get(profile_url)
        
        # Should be accessible after login
        self.assertEqual(response.status_code, 200) 