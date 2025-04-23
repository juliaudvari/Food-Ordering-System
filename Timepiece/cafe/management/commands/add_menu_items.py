from django.core.management.base import BaseCommand
from cafe.models import Category, MenuItem
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add sample menu items to the database'

    def handle(self, *args, **options):
        coffee_category, created = Category.objects.get_or_create(
            name='Coffee',
            defaults={'description': 'Our premium coffee selection, sourced from the finest beans around the world.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {coffee_category}'))
        
        tea_category, created = Category.objects.get_or_create(
            name='Tea',
            defaults={'description': 'Exquisite teas from around the world, offering a variety of flavors and aromas.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {tea_category}'))
        
        pastry_category, created = Category.objects.get_or_create(
            name='Pastries',
            defaults={'description': 'Freshly baked pastries made daily in our kitchen.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {pastry_category}'))
        
        sandwich_category, created = Category.objects.get_or_create(
            name='Sandwiches',
            defaults={'description': 'Delicious sandwiches prepared with fresh ingredients.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {sandwich_category}'))

        dessert_category, created = Category.objects.get_or_create(
            name='Desserts',
            defaults={'description': 'Sweet treats to satisfy your cravings.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {dessert_category}'))

        menu_items = [
            {
                'name': 'Espresso',
                'description': 'A concentrated shot of coffee with a rich flavor and crema on top.',
                'price': Decimal('2.50'),
                'category': coffee_category,
                'is_available': True
            },
            {
                'name': 'Cappuccino',
                'description': 'Espresso with steamed milk and a generous layer of foam.',
                'price': Decimal('3.50'),
                'category': coffee_category,
                'is_available': True
            },
            {
                'name': 'Latte',
                'description': 'Smooth espresso with steamed milk and a light layer of foam.',
                'price': Decimal('3.75'),
                'category': coffee_category,
                'is_available': True
            },
            {
                'name': 'Mocha',
                'description': 'Espresso with chocolate syrup, steamed milk, and whipped cream.',
                'price': Decimal('4.25'),
                'category': coffee_category,
                'is_available': True
            },
            {
                'name': 'Cold Brew',
                'description': 'Coffee brewed with cold water over 12-24 hours, resulting in a smooth, less acidic flavor.',
                'price': Decimal('4.00'),
                'category': coffee_category,
                'is_available': True
            },
            
            {
                'name': 'Earl Grey',
                'description': 'Black tea flavored with oil of bergamot, offering a fragrant and refreshing taste.',
                'price': Decimal('3.00'),
                'category': tea_category,
                'is_available': True
            },
            {
                'name': 'Green Tea',
                'description': 'Light, refreshing tea with antioxidant properties.',
                'price': Decimal('3.00'),
                'category': tea_category,
                'is_available': True
            },
            {
                'name': 'Chamomile',
                'description': 'Herbal tea known for its calming properties.',
                'price': Decimal('3.25'),
                'category': tea_category,
                'is_available': True
            },
            {
                'name': 'Chai Latte',
                'description': 'Spiced black tea with steamed milk.',
                'price': Decimal('4.00'),
                'category': tea_category,
                'is_available': True
            },
            
            {
                'name': 'Croissant',
                'description': 'Buttery, flaky pastry with a golden-brown crust.',
                'price': Decimal('2.75'),
                'category': pastry_category,
                'is_available': True
            },
            {
                'name': 'Pain au Chocolat',
                'description': 'Chocolate-filled croissant-like pastry.',
                'price': Decimal('3.25'),
                'category': pastry_category,
                'is_available': True
            },
            {
                'name': 'Cinnamon Roll',
                'description': 'Sweet roll with cinnamon filling and cream cheese frosting.',
                'price': Decimal('3.50'),
                'category': pastry_category,
                'is_available': True
            },
            {
                'name': 'Scone',
                'description': 'Slightly sweet baked good with a crumbly texture.',
                'price': Decimal('2.50'),
                'category': pastry_category,
                'is_available': True
            },
            
            {
                'name': 'Avocado Toast',
                'description': 'Toasted artisan bread topped with mashed avocado, salt, pepper, and red pepper flakes.',
                'price': Decimal('7.50'),
                'category': sandwich_category,
                'is_available': True
            },
            {
                'name': 'Chicken Panini',
                'description': 'Grilled chicken, mozzarella, roasted red peppers, and pesto on pressed ciabatta bread.',
                'price': Decimal('8.25'),
                'category': sandwich_category,
                'is_available': True
            },
            {
                'name': 'Vegetarian Wrap',
                'description': 'Hummus, mixed greens, cucumber, tomato, and avocado in a whole wheat wrap.',
                'price': Decimal('7.75'),
                'category': sandwich_category,
                'is_available': True
            },
            {
                'name': 'Club Sandwich',
                'description': 'Triple-decker sandwich with turkey, bacon, lettuce, tomato, and mayo.',
                'price': Decimal('9.00'),
                'category': sandwich_category,
                'is_available': True
            },
            
            {
                'name': 'Chocolate Cake',
                'description': 'Rich, moist chocolate cake with chocolate ganache.',
                'price': Decimal('5.50'),
                'category': dessert_category,
                'is_available': True
            },
            {
                'name': 'Cheesecake',
                'description': 'Creamy classic cheesecake with a graham cracker crust.',
                'price': Decimal('5.75'),
                'category': dessert_category,
                'is_available': True
            },
            {
                'name': 'Tiramisu',
                'description': 'Italian dessert made with coffee-soaked ladyfingers and mascarpone cream.',
                'price': Decimal('6.00'),
                'category': dessert_category,
                'is_available': True
            },
            {
                'name': 'Apple Pie',
                'description': 'Warm apple pie with a flaky crust, served with vanilla ice cream.',
                'price': Decimal('5.25'),
                'category': dessert_category,
                'is_available': True
            }
        ]

        for item_data in menu_items:
            menu_item, created = MenuItem.objects.get_or_create(
                name=item_data['name'],
                category=item_data['category'],
                defaults={
                    'description': item_data['description'],
                    'price': item_data['price'],
                    'is_available': item_data['is_available']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created menu item: {menu_item}'))
            else:
                self.stdout.write(self.style.WARNING(f'Menu item already exists: {menu_item}')) 