from django.test import TestCase
from django.contrib.auth.models import User
from cafe.models import Category, MenuItem, CustomerProfile, Order, OrderItem, Payment, Review
from decimal import Decimal
import uuid

class CategoryModelTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Coffee",
            description="Various coffee drinks"
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, "Coffee")
        self.assertEqual(self.category.description, "Various coffee drinks")
    
    def test_category_str(self):
        self.assertEqual(str(self.category), "Coffee")

class MenuItemModelTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Coffee")
        self.menu_item = MenuItem.objects.create(
            name="Espresso",
            description="Strong coffee",
            price=Decimal('2.50'),
            category=self.category,
            is_available=True
        )
    
    def test_menu_item_creation(self):
        self.assertEqual(self.menu_item.name, "Espresso")
        self.assertEqual(self.menu_item.description, "Strong coffee")
        self.assertEqual(self.menu_item.price, Decimal('2.50'))
        self.assertEqual(self.menu_item.category, self.category)
        self.assertTrue(self.menu_item.is_available)
    
    def test_menu_item_str(self):
        self.assertEqual(str(self.menu_item), "Espresso")

class CustomerProfileModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User"
        )
        self.profile = CustomerProfile.objects.create(
            user=self.user,
            phone_number="1234567890",
            address="123 Test St"
        )
    
    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.phone_number, "1234567890")
        self.assertEqual(self.profile.address, "123 Test St")
    
    def test_profile_str(self):
        self.assertEqual(str(self.profile), "Test User")

class OrderModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.order_number = uuid.uuid4()
        self.order = Order.objects.create(
            customer=self.user,
            status="PENDING",
            total_amount=Decimal('10.00'),
            notes="Test order",
            order_number=self.order_number
        )
    
    def test_order_creation(self):
        self.assertEqual(self.order.customer, self.user)
        self.assertEqual(self.order.status, "PENDING")
        self.assertEqual(self.order.total_amount, Decimal('10.00'))
        self.assertEqual(self.order.notes, "Test order")
        self.assertEqual(self.order.order_number, self.order_number)
    
    def test_order_str(self):
        expected = f"Order #{self.order_number} - testuser"
        self.assertEqual(str(self.order), expected)
    
    def test_get_absolute_url(self):
        expected = f"/orders/{self.order.id}/"
        self.assertEqual(self.order.get_absolute_url(), expected)

class OrderItemModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.category = Category.objects.create(name="Coffee")
        self.menu_item = MenuItem.objects.create(
            name="Espresso",
            description="Strong coffee",
            price=Decimal('2.50'),
            category=self.category
        )
        self.order = Order.objects.create(
            customer=self.user,
            status="PENDING",
            total_amount=Decimal('5.00')
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            quantity=2,
            price=Decimal('2.50')
        )
    
    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.menu_item, self.menu_item)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, Decimal('2.50'))
    
    def test_order_item_str(self):
        self.assertEqual(str(self.order_item), "2 x Espresso")
    
    def test_subtotal_property(self):
        self.assertEqual(self.order_item.subtotal, Decimal('5.00'))

class PaymentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.order = Order.objects.create(
            customer=self.user,
            status="PENDING",
            total_amount=Decimal('10.00')
        )
        self.payment = Payment.objects.create(
            order=self.order,
            payment_method="CREDIT_CARD",
            amount=Decimal('10.00'),
            transaction_id="txn_123456"
        )
    
    def test_payment_creation(self):
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(self.payment.payment_method, "CREDIT_CARD")
        self.assertEqual(self.payment.amount, Decimal('10.00'))
        self.assertEqual(self.payment.transaction_id, "txn_123456")
    
    def test_payment_str(self):
        expected = f"Payment for Order #{self.order.order_number}"
        self.assertEqual(str(self.payment), expected)

class ReviewModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.category = Category.objects.create(name="Coffee")
        self.menu_item = MenuItem.objects.create(
            name="Espresso",
            description="Strong coffee",
            price=Decimal('2.50'),
            category=self.category
        )
        self.review = Review.objects.create(
            customer=self.user,
            menu_item=self.menu_item,
            rating=5,
            comment="Excellent coffee!"
        )
    
    def test_review_creation(self):
        self.assertEqual(self.review.customer, self.user)
        self.assertEqual(self.review.menu_item, self.menu_item)
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, "Excellent coffee!")
    
    def test_review_str(self):
        expected = f"testuser's review for Espresso"
        self.assertEqual(str(self.review), expected) 