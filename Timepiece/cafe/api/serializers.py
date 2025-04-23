from rest_framework import serializers
from cafe.models import Category, MenuItem, CustomerProfile, Order, OrderItem, Payment, Review, SupportRequest, SupportMessage
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'price', 'image', 
            'category', 'category_id', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'phone_number', 'address']
        read_only_fields = ['id']

class ReviewSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        write_only=True,
        source='menu_item'
    )
    
    class Meta:
        model = Review
        fields = ['id', 'customer', 'menu_item', 'menu_item_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'customer', 'created_at']
    
    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        write_only=True,
        source='menu_item'
    )
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id', 'price', 'subtotal']
    
    def create(self, validated_data):
        menu_item = validated_data['menu_item']
        validated_data['price'] = menu_item.price
        return super().create(validated_data)

class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    order_items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'order_date', 'status', 'total_amount', 
            'notes', 'order_number', 'items', 'order_items'
        ]
        read_only_fields = ['id', 'customer', 'order_date', 'order_number', 'total_amount']
    
    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items', [])
        validated_data['customer'] = self.context['request'].user
        
        validated_data['total_amount'] = 0
        
        order = super().create(validated_data)
        
        total_amount = 0
        for item_data in order_items_data:
            menu_item_id = item_data.get('menu_item_id')
            quantity = item_data.get('quantity', 1)
            
            menu_item = MenuItem.objects.get(id=menu_item_id)
            price = menu_item.price
            
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=price
            )
            
            total_amount += price * quantity
        
        order.total_amount = total_amount
        order.save()
        
        return order

class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        write_only=True,
        source='order'
    )
    
    class Meta:
        model = Payment
        fields = ['id', 'order', 'order_id', 'amount', 'payment_method', 'transaction_id', 'payment_date', 'status']
        read_only_fields = ['id', 'transaction_id', 'payment_date', 'status']
    
    def validate(self, data):
        if data['amount'] != data['order'].total_amount:
            raise serializers.ValidationError("Payment amount must match order total")
        return data

class SupportMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = SupportMessage
        fields = ['id', 'support_request', 'sender', 'message', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

class SupportRequestSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    messages = SupportMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupportRequest
        fields = ['id', 'customer', 'subject', 'description', 'status', 
                  'created_at', 'updated_at', 'resolved_at', 'assigned_to', 'messages']
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at', 'resolved_at', 'assigned_to']
    
    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data) 