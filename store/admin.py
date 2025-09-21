from django.contrib import admin

from .models import Product, Order, OrderItem, CartItem, Cart, Inventory

# Register your models here.
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Inventory)
