from django.core.management.base import BaseCommand
from store.models import Product, StockBalance
import json


class Command(BaseCommand):
    help = 'Load products data from JSON file'

    def handle(self, *args, **options):
        try:
            with open('products_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

                for item in data:
                    product, created = Product.objects.get_or_create(
                        name=item['name'],
                        defaults={
                            'description': item.get('description', ''),
                            'price': item['price'],
                            'is_active': True
                        }
                    )

                    StockBalance.objects.update_or_create(
                        product=product,
                        defaults={'quantity': item['quantity']}
                    )

                self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(data)} products'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))