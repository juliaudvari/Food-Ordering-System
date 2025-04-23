from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import uuid

class Category(models.Model):
    # Category model to organize menu items as required by the menu management requirement
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    # Core menu functionality as specified in requirements - manages the cafe's food and drink items
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Price tracking for sales and ordering
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)  # Supporting visual menu display requirement
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')  # Hierarchical organization
    is_available = models.BooleanField(default=True)  # Supports inventory management requirement
    created_at = models.DateTimeField(auto_now_add=True)  # Audit trail for menu changes
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class CustomerProfile(models.Model):
    # Customer profile for extended user information beyond Django's built-in User model
    # Satisfies the user management requirement for customer information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Contact info for order follow-up
    address = models.TextField(blank=True, null=True)  # Delivery information for future functionality
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Order(models.Model):
    # Order processing system - central to the cafe's operations
    # Implements the order management requirement with status tracking
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),  # Initial state when customer places order
        ('PROCESSING', 'Processing'),  # Staff has seen and is working on order
        ('COMPLETED', 'Completed'),  # Order fulfilled and delivered to customer
        ('CANCELLED', 'Cancelled'),  # Order canceled by customer or staff
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')  # Links order to customer
    order_date = models.DateTimeField(default=timezone.now)  # Timestamp for order analytics
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')  # Status workflow tracking
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Order total for financial reporting
    notes = models.TextField(blank=True, null=True)  # Customer special requests or dietary needs
    order_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)  # Public-facing order identifier
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.username}"
    
    def get_absolute_url(self):
        return reverse('cafe:order_detail', args=[str(self.id)])

class OrderItem(models.Model):
    # Individual line items within an order - supports the itemized ordering requirement
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # Parent order
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)  # Item being ordered
    quantity = models.PositiveIntegerField(default=1)  # How many of this item
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Price at time of order (may differ from current menu price)
    
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity  # Calculate line item total for order summary

class Payment(models.Model):
    # Payment tracking system - supports the financial transaction requirement
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),  # Traditional payment method
        ('CREDIT_CARD', 'Credit Card'),  # Card processing
        ('DEBIT_CARD', 'Debit Card'),  # Direct bank payment
        ('PAYPAL', 'PayPal'),  # Online payment option
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')  # Order being paid for
    payment_date = models.DateTimeField(default=timezone.now)  # When payment was processed
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)  # How customer paid
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Payment amount for reconciliation
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # External payment reference
    
    def __str__(self):
        return f"Payment for Order #{self.order.order_number}"

class Review(models.Model):
    # Customer feedback system - implements the review management requirement
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')  # Who left the review
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='reviews')  # Item being reviewed
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 5-star rating system
    comment = models.TextField(blank=True, null=True)  # Detailed feedback
    created_at = models.DateTimeField(auto_now_add=True)  # When review was submitted
    
    class Meta:
        unique_together = ('customer', 'menu_item')  # Prevent duplicate reviews
    
    def __str__(self):
        return f"{self.customer.username}'s review for {self.menu_item.name}"

class SupportRequest(models.Model):
    # Customer support ticket system - implements the customer service requirement
    STATUS_CHOICES = [
        ('OPEN', 'Open'),  # New request awaiting staff attention
        ('IN_PROGRESS', 'In Progress'),  # Staff working on resolution
        ('RESOLVED', 'Resolved'),  # Issue addressed by staff
        ('CLOSED', 'Closed'),  # Final state after customer confirmation
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_requests')  # Customer with issue
    subject = models.CharField(max_length=200)  # Brief description of problem
    description = models.TextField()  # Detailed explanation of issue
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')  # Request status
    created_at = models.DateTimeField(auto_now_add=True)  # When request was submitted
    updated_at = models.DateTimeField(auto_now=True)  # Last activity timestamp
    resolved_at = models.DateTimeField(null=True, blank=True)  # When marked as resolved
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_support_requests')  # Staff member handling case
    
    def __str__(self):
        return f"Support Request #{self.id} - {self.subject}"
    
    def get_absolute_url(self):
        return reverse('cafe:support_request_detail', args=[str(self.id)])

class SupportMessage(models.Model):
    # Communication thread for support requests - enables ongoing customer/staff dialogue
    support_request = models.ForeignKey(SupportRequest, on_delete=models.CASCADE, related_name='messages')  # Parent support ticket
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_support_messages')  # Message author
    message = models.TextField()  # Message content
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for conversation flow
    
    def __str__(self):
        return f"Message from {self.sender.username} on Support Request #{self.support_request.id}"
