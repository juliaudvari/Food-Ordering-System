from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'menu-items', views.MenuItemViewSet)
router.register(r'profiles', views.CustomerProfileViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'order-items', views.OrderItemViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'support-requests', views.SupportRequestViewSet, basename='support-request')
router.register(r'support-messages', views.SupportMessageViewSet, basename='support-message')

urlpatterns = [
    path('', include(router.urls)),
]