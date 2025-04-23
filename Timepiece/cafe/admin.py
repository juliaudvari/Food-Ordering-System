from django.contrib import admin
from .models import Category, MenuItem, CustomerProfile, Order, OrderItem, Payment, Review, SupportRequest, SupportMessage

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'order_date', 'status', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('order_number', 'customer__username', 'customer__email')
    inlines = [OrderItemInline]

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'user__email', 'phone_number')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('order__order_number', 'transaction_id')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'menu_item', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment',)

class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0

class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'customer', 'status', 'created_at', 'assigned_to')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'description')
    inlines = [SupportMessageInline]

admin.site.register(Category, CategoryAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(CustomerProfile, CustomerProfileAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(SupportRequest, SupportRequestAdmin)
admin.site.register(SupportMessage)
