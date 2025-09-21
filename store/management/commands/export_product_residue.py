from django.core.management.base import BaseCommand
from store.models import StockBalance
import json


class Command(BaseCommand):
    help = 'Export stock balances to JSON file'

    def handle(self, *args, **options):
        balances = StockBalance.objects.select_related('product').all()
        data = []

        for balance in balances:
            data.append({
                'product_id': balance.product.id,
                'product_name': balance.product.name,
                'quantity': balance.quantity,
                'last_updated': balance.last_updated.strftime('%Y-%m-%d %H:%M:%S')
            })

        with open('stock_balances.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        self.stdout.write(self.style.SUCCESS(f'Successfully exported {len(data)} stock balances'))