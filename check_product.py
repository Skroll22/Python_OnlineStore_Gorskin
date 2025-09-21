import os
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyOnlineStore.settings')
django.setup()

from store.models import Product

# Проверка товара
slug_to_check = "apple-iphone-15-pro-max-256gb-grey"
product = Product.objects.filter(slug=slug_to_check).first()

if product:
    print(f"Товар найден: {product.name}")
    print(f"ID: {product.id}")
    print(f"Активен: {product.is_active}")
    print(f"Изображение: {product.image.url if product.image else 'нет'}")
else:
    print("Товар не найден!")