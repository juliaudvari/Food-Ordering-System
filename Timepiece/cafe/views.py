from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import F, Sum
from decimal import Decimal
from .forms import UserRegistrationForm, CustomerProfileForm, SupportRequestForm, SupportMessageForm
from .models import Category, MenuItem, Order, OrderItem, SupportRequest, SupportMessage, Payment
from django.template.loader import render_to_string
from django.utils.html import escape

def home(request):
    # Homepage view that displays featured menu items - satisfies the browsing requirement
    categories = Category.objects.all()
    featured_items = MenuItem.objects.filter(is_available=True)[:6]
    
    context = {
        'categories': categories,
        'featured_items': featured_items,
    }
    
    return render(request, 'cafe/home.html', context)

def about(request):
    # About page view - part of the static content requirement
    return render(request, 'cafe/about.html')

def newsletter_signup(request):
    # Newsletter signup functionality - part of the marketing requirement
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # In a real implementation, would integrate with an email service
            messages.success(request, "Thank you for signing up for our newsletter!")
        else:
            messages.error(request, "Please enter a valid email address.")
    
    return redirect('cafe:home')

def menu(request, category_id=None):
    # Menu browsing view with filtering options - core browse feature from use cases
    categories = Category.objects.all().order_by('name')
    
    filters = {}
    active_category = None
    
    if category_id:
        # Filter by direct category ID in URL
        active_category = get_object_or_404(Category, id=category_id)
        filters['category'] = active_category
    elif request.GET.get('category'):
        # Filter by category ID in query parameters
        try:
            category_id = int(request.GET.get('category'))
            active_category = Category.objects.get(id=category_id)
            filters['category'] = active_category
        except (ValueError, Category.DoesNotExist):
            pass
    
    if request.GET.get('search'):
        # Search functionality for menu items - addressing search requirement
        search_query = request.GET.get('search')
        filters['name__icontains'] = search_query
    
    if request.GET.get('price_min'):
        # Price range filter - minimum
        try:
            price_min = float(request.GET.get('price_min'))
            filters['price__gte'] = price_min
        except ValueError:
            pass
    
    if request.GET.get('price_max'):
        # Price range filter - maximum
        try:
            price_max = float(request.GET.get('price_max'))
            filters['price__lte'] = price_max
        except ValueError:
            pass
    
    if request.GET.get('vegetarian'):
        # Dietary preference filter - vegetarian
        filters['is_vegetarian'] = True
    
    if request.GET.get('vegan'):
        # Dietary preference filter - vegan
        filters['is_vegan'] = True
    
    if request.GET.get('gluten_free'):
        # Dietary preference filter - gluten free
        filters['is_gluten_free'] = True
    
    # Only show available items - inventory management feature
    filters['is_available'] = True
    
    menu_items = MenuItem.objects.filter(**filters).order_by('category', 'name')
    
    context = {
        'categories': categories,
        'active_category': active_category,
        'menu_items': menu_items,
    }
    
    return render(request, 'cafe/menu.html', context)

def menu_item_detail(request, item_id):
    # Detailed item view - supports the detailed product information requirement
    menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    related_items = MenuItem.objects.filter(category=menu_item.category, is_available=True).exclude(id=item_id)[:4]
    
    context = {
        'menu_item': menu_item,
        'related_items': related_items
    }
    
    return render(request, 'cafe/menu_item_detail.html', context)

@login_required
def support_request_list(request):
    # Support ticket listing - implements customer service requirement
    if request.user.is_staff:
        # Staff members can see all requests
        support_requests = SupportRequest.objects.all().order_by('-created_at')
    else:
        # Customers can only see their own requests
        support_requests = SupportRequest.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'support_requests': support_requests
    }
    
    return render(request, 'cafe/support_request_list.html', context)

@login_required
def support_request_detail(request, request_id):
    # Support ticket details view with messaging - customer service requirement
    support_request = get_object_or_404(SupportRequest, id=request_id)
    
    # Security check - only allow staff or the ticket owner to view
    if not request.user.is_staff and request.user != support_request.customer:
        messages.error(request, "You don't have permission to view this support request.")
        return redirect('cafe:support_request_list')
    
    if request.method == 'POST':
        # Handle adding new message to the support thread
        message_text = request.POST.get('message', '').strip()
        if message_text:
            SupportMessage.objects.create(
                support_request=support_request,
                sender=request.user,
                message=message_text
            )
            
            # Update the last activity timestamp
            support_request.updated_at = timezone.now()
            # Reopen resolved tickets if customer responds
            if support_request.status == 'RESOLVED' and request.user == support_request.customer:
                support_request.status = 'OPEN'
            support_request.save()
            
            messages.success(request, "Your message has been sent.")
            return redirect('cafe:support_request_detail', request_id=request_id)
        else:
            messages.error(request, "Message cannot be empty.")
    
    # Get all messages in chronological order
    support_messages = support_request.messages.all().order_by('created_at')
    
    context = {
        'support_request': support_request,
        'support_messages': support_messages
    }
    
    return render(request, 'cafe/support_request_detail.html', context)

@login_required
def support_request_create(request):
    # Support ticket creation view - customer service requirement
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        
        if subject and description:
            support_request = SupportRequest.objects.create(
                customer=request.user,
                subject=subject,
                description=description,
                status='OPEN'
            )
            messages.success(request, "Your support request has been submitted successfully.")
            return redirect('cafe:support_request_detail', request_id=support_request.id)
        else:
            messages.error(request, "Please fill in all required fields.")
    
    return render(request, 'cafe/support_request_form.html')

@login_required
def support_request_update(request, request_id):
    # Support ticket status update - staff functionality for customer service
    support_request = get_object_or_404(SupportRequest, id=request_id)
    
    # Security check - only staff or assigned staff can update
    if not request.user.is_staff and request.user != support_request.assigned_to:
        messages.error(request, "You don't have permission to update this support request.")
        return redirect('cafe:support_request_list')
    
    if request.method == 'POST':
        # Handle status updates
        new_status = request.POST.get('status')
        if new_status in [status[0] for status in SupportRequest.STATUS_CHOICES]:
            support_request.status = new_status
            if new_status == 'RESOLVED':
                support_request.resolved_at = timezone.now()
            support_request.save()
            messages.success(request, "Support request status has been updated.")
        
        # Handle staff assignment
        if request.user.is_staff and 'assign' in request.POST:
            support_request.assigned_to = request.user
            support_request.status = 'IN_PROGRESS'
            support_request.save()
            messages.success(request, "Support request has been assigned to you.")
            
        return redirect('cafe:support_request_detail', request_id=request_id)
    
    context = {
        'support_request': support_request,
    }
    
    return render(request, 'cafe/support_request_update.html', context)

def register(request):
    # User registration view - user management requirement
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to Timepiece Cafe!")
            return redirect('cafe:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def register_simple(request):
    # Alternative registration view with simplified template
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to Timepiece Cafe!")
            return redirect('cafe:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register_simple.html', {'form': form})

def register_direct(request):
    # Direct HTML registration view for demonstration purposes
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to Timepiece Cafe!")
            return redirect('cafe:home')
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            error_html = "<br>".join(escape(msg) for msg in error_messages)
    else:
        form = UserRegistrationForm()
        error_html = ""
    
    # Direct HTML template rendered without a template file
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - Timepiece Cafe</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body>
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <h2 class="mb-4">Register</h2>
                    
                    {error_html and f'<div class="alert alert-danger">{error_html}</div>' or ''}
                    
                    <form method="post" action="">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{escape(request.META.get('CSRF_COOKIE', ''))}">
                        
                        <div class="mb-3">
                            <label for="id_username" class="form-label">Username</label>
                            <input type="text" name="username" id="id_username" class="form-control" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_email" class="form-label">Email</label>
                            <input type="email" name="email" id="id_email" class="form-control" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_first_name" class="form-label">First Name</label>
                            <input type="text" name="first_name" id="id_first_name" class="form-control" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_last_name" class="form-label">Last Name</label>
                            <input type="text" name="last_name" id="id_last_name" class="form-control" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_password1" class="form-label">Password</label>
                            <input type="password" name="password1" id="id_password1" class="form-control" required>
                            <div class="form-text">
                                <ul class="list-unstyled">
                                    <li>Your password can't be too similar to your other personal information.</li>
                                    <li>Your password must contain at least 8 characters.</li>
                                    <li>Your password can't be a commonly used password.</li>
                                    <li>Your password can't be entirely numeric.</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_password2" class="form-label">Confirm Password</label>
                            <input type="password" name="password2" id="id_password2" class="form-control" required>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">Register</button>
                    </form>
                    
                    <div class="mt-3">
                        <p>Already have an account? <a href="/accounts/login/">Log in</a></p>
                    </div>
                    
                    <div class="mt-3">
                        <a href="/" class="btn btn-outline-secondary">Back to Home</a>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HttpResponse(html)

def get_cart(request):
    # Helper function to get or initialize the shopping cart in session
    cart = request.session.get('cart', {})
    if not cart:
        request.session['cart'] = {}
    return request.session['cart']

def add_to_cart(request, item_id):
    # Add item to cart functionality - implements ordering requirement
    cart = get_cart(request)
    menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    item_id_str = str(item_id)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Update quantity if item already in cart, otherwise add new entry
    if item_id_str in cart:
        cart[item_id_str]['quantity'] += quantity
    else:
        cart[item_id_str] = {
            'quantity': quantity,
            'price': str(menu_item.price),
            'name': menu_item.name
        }
    
    request.session.modified = True
    messages.success(request, f"{menu_item.name} added to your cart.")
    
    next_url = request.POST.get('next', 'cafe:cart')
    return redirect(next_url)

def update_cart_item(request, item_id):
    # Update cart item quantity - part of cart management requirement
    cart = get_cart(request)
    item_id_str = str(item_id)
    
    if item_id_str in cart:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart[item_id_str]['quantity'] = quantity
            messages.success(request, "Cart updated.")
        else:
            return remove_from_cart(request, item_id)
    
    request.session.modified = True
    return redirect('cafe:cart')

def remove_from_cart(request, item_id):
    # Remove item from cart - part of cart management requirement
    cart = get_cart(request)
    item_id_str = str(item_id)
    
    if item_id_str in cart:
        item_name = cart[item_id_str]['name']
        del cart[item_id_str]
        request.session.modified = True
        messages.success(request, f"{item_name} removed from your cart.")
    
    return redirect('cafe:cart')

def cart_view(request):
    # Cart viewing functionality - displays current order items and total
    # Implements part of the shopping cart requirement
    cart = get_cart(request)
    cart_items = []
    total = Decimal('0.00')
    
    for item_id, item_data in cart.items():
        price = Decimal(item_data['price'])
        quantity = item_data['quantity']
        subtotal = price * quantity
        total += subtotal
        
        cart_items.append({
            'id': item_id,
            'name': item_data['name'],
            'price': price,
            'quantity': quantity,
            'subtotal': subtotal
        })
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    
    return render(request, 'cafe/cart.html', context)

@login_required
def checkout(request):
    # Checkout process - implements order creation from cart
    # Core part of the ordering requirement
    cart = get_cart(request)
    
    # Prevent empty checkouts
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cafe:cart')
    
    if request.method == 'POST':
        # Process checkout form submission
        total_amount = Decimal('0.00')
        
        # Calculate total from cart items
        for item_id, item_data in cart.items():
            price = Decimal(item_data['price'])
            quantity = item_data['quantity']
            total_amount += price * quantity
        
        notes = request.POST.get('notes', '')
        
        # Create the order record
        order = Order.objects.create(
            customer=request.user,
            total_amount=total_amount,
            notes=notes
        )
        
        # Create order items from cart contents
        for item_id, item_data in cart.items():
            menu_item = get_object_or_404(MenuItem, id=item_id)
            price = Decimal(item_data['price'])
            quantity = item_data['quantity']
            
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=price
            )
        
        # Clear the cart after successful order
        request.session['cart'] = {}
        request.session.modified = True
        
        # Demo payment creation - in production would integrate with payment gateway
        Payment.objects.create(
            order=order,
            amount=total_amount,
            payment_method='ONLINE',
            transaction_id=f"DEMO-{order.order_number}",
            status='COMPLETED'
        )
        
        messages.success(request, f"Your order has been placed successfully! Order number: {order.order_number}")
        return redirect('cafe:order_detail', order_number=order.order_number)
    
    # Prepare cart items for checkout display
    cart_items = []
    total = Decimal('0.00')
    
    for item_id, item_data in cart.items():
        price = Decimal(item_data['price'])
        quantity = item_data['quantity']
        subtotal = price * quantity
        total += subtotal
        
        cart_items.append({
            'id': item_id,
            'name': item_data['name'],
            'price': price,
            'quantity': quantity,
            'subtotal': subtotal
        })
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    
    return render(request, 'cafe/checkout.html', context)

@login_required
def order_list(request):
    # Order history view - implements order tracking requirement
    orders = Order.objects.filter(customer=request.user).order_by('-order_date')
    
    context = {
        'orders': orders
    }
    
    return render(request, 'cafe/order_list.html', context)

@login_required
def order_detail(request, order_number):
    # Order details view - implements detailed order information requirement
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    order_items = order.items.all().select_related('menu_item')
    payment = Payment.objects.filter(order=order).first()
    
    context = {
        'order': order,
        'order_items': order_items,
        'payment': payment
    }
    
    return render(request, 'cafe/order_detail.html', context)
