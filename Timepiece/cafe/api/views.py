from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from cafe.models import Category, MenuItem, CustomerProfile, Order, OrderItem, Payment, Review, SupportRequest, SupportMessage
from .serializers import (
    CategorySerializer, MenuItemSerializer, CustomerProfileSerializer,
    OrderSerializer, OrderItemSerializer, PaymentSerializer, ReviewSerializer,
    SupportRequestSerializer, SupportMessageSerializer
)
import logging
from django.utils import timezone

security_logger = logging.getLogger('security')

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'customer'):
            return obj.customer == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        menu_item = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        security_logger.info(f"User {user.username} attempted to toggle favorite for menu item {menu_item.id}")
        
        return Response({"success": True, "is_favorite": True})

class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomerProfile.objects.all()
        return CustomerProfile.objects.filter(user=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['menu_item', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def perform_create(self, serializer):
        security_logger.info(f"User {self.request.user.username} is creating a review")
        serializer.save(customer=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['order_date']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=self.request.user)
    
    def perform_create(self, serializer):
        security_logger.info(f"User {self.request.user.username} is creating an order")
        serializer.save(customer=self.request.user)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__customer=self.request.user)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'status']
    ordering_fields = ['payment_date']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__customer=self.request.user)
    
    def perform_create(self, serializer):
        security_logger.info(f"User {self.request.user.username} is making a payment")
        serializer.save()

class SupportRequestViewSet(viewsets.ModelViewSet):
    serializer_class = SupportRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SupportRequest.objects.all()
        return SupportRequest.objects.filter(customer=user)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        if not request.user.is_staff:
            return Response({"error": "Only staff can assign support requests"}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        support_request = self.get_object()
        support_request.assigned_to = request.user
        support_request.status = 'IN_PROGRESS'
        support_request.save()
        
        serializer = self.get_serializer(support_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        if not request.user.is_staff and request.user != self.get_object().assigned_to:
            return Response({"error": "Only staff or assigned agent can resolve support requests"}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        support_request = self.get_object()
        support_request.status = 'RESOLVED'
        support_request.resolved_at = timezone.now()
        support_request.save()
        
        serializer = self.get_serializer(support_request)
        return Response(serializer.data)

class SupportMessageViewSet(viewsets.ModelViewSet):
    serializer_class = SupportMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SupportMessage.objects.all()
        return SupportMessage.objects.filter(support_request__customer=user)