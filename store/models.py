from django.db import models
from django.utils.text import slugify
from django.urls import reverse

from MyOnlineStore import settings


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to="products/", verbose_name="Изображение", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        return f"{self.product.name} - {self.quantity} шт."

    class Meta:
        verbose_name = "Складской запас"
        verbose_name_plural = "Складские запасы"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('processing', 'В процессе'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Покупатель")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма заказа")
    shipping_address = models.TextField(verbose_name="Адрес доставки")

    def __str__(self):
        return f"Заказ №{self.id} - {self.customer}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def create_order_from_cart(self, cart):
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=self,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        cart.items.all().delete()
        self.update_total()

    def update_total(self):
        self.total_amount = sum(item.price * item.quantity for item in self.items.all())
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

class Cart(models.Model):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Покупатель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Корзина {self.customer}"

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    @property
    def total_price(self):
        return sum(item.price for item in self.items.all())

    def add_product(self, product, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def add_product(self, product, quantity=1):
        """Делегируем добавление товара сервису"""
        from .services import CartService
        return CartService.add_to_cart(self, product.id, quantity)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def price(self):
        return self.product.price * self.quantity

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"

class StockBalance(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_balance'
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        return f"{self.product.name} - {self.quantity} шт."

    class Meta:
        verbose_name = "Остаток товара"
        verbose_name_plural = "Остатки товаров"