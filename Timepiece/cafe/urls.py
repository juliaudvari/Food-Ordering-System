from django.urls import path
from . import views

app_name = 'cafe'

urlpatterns = [
    # Core navigation and information pages
    path('', views.home, name='home'),  # Homepage with featured items - browsing requirement
    path('about/', views.about, name='about'),  # About page - static content requirement
    
    # Menu browsing functionality - core product browsing requirement
    path('menu/', views.menu, name='menu'),  # Full menu with filtering options
    path('menu/category/<int:category_id>/', views.menu, name='menu_category'),  # Category filtering
    path('menu/item/<int:item_id>/', views.menu_item_detail, name='menu_item_detail'),  # Detailed item view
    
    # Marketing feature - newsletter subscription
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),  # Marketing requirement
    
    # Customer support system - customer service requirement
    path('support/', views.support_request_list, name='support_request_list'),  # View support tickets
    path('support/create/', views.support_request_create, name='support_request_create'),  # Create support ticket
    path('support/<int:request_id>/', views.support_request_detail, name='support_request_detail'),  # View specific ticket
    path('support/<int:request_id>/update/', views.support_request_update, name='support_request_update'),  # Update ticket status
    
    # Shopping cart functionality - ordering requirement
    path('cart/', views.cart_view, name='cart'),  # View current cart
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),  # Add item to cart
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Remove item from cart
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),  # Update item quantity
    
    # Checkout and order management - order processing requirement
    path('checkout/', views.checkout, name='checkout'),  # Process order from cart
    path('orders/', views.order_list, name='order_list'),  # View order history
    path('orders/<uuid:order_number>/', views.order_detail, name='order_detail'),  # View order details
    
    # User account management - authentication requirement
    path('register/', views.register, name='register'),  # Standard registration
    path('register-simple/', views.register_simple, name='register_simple'),  # Simplified registration
    path('register-direct/', views.register_direct, name='register_direct'),  # Direct HTML registration
] 