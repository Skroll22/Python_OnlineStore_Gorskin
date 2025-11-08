from django.core.exceptions import ValidationError
from .models import Order, Cart, CartItem, Product, StockBalance


class OrderService:
    """Сервис для работы с заказами"""

    @staticmethod
    def process_order(order_id, shipping_address):
        """
        Обработка заказа - изолированная функция
        """
        try:
            order = Order.objects.get(id=order_id)
            order.shipping_address = shipping_address
            order.status = 'processing'
            order.save()
            return order
        except Order.DoesNotExist:
            raise ValidationError("Заказ не найден")

    @staticmethod
    def get_orders_by_status(status):
        """
        Получение заказов по статусу
        """
        return Order.objects.filter(status=status).order_by('-order_date')

    @staticmethod
    def cancel_order(order_id):
        """
        Отмена заказа
        """
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'cancelled'
            order.save()
            return order
        except Order.DoesNotExist:
            raise ValidationError("Заказ не найден")


class CartService:
    """Сервис для работы с корзиной"""

    @staticmethod
    def add_to_cart(cart, product_id, quantity=1):
        """
        Добавление товара в корзину - изолированная функция
        """
        try:
            product = Product.objects.get(id=product_id, is_active=True)

            # Проверяем наличие на складе
            stock_balance = StockBalance.objects.filter(product=product).first()
            if stock_balance and stock_balance.quantity < quantity:
                raise ValidationError("Недостаточно товара на складе")

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return cart_item
        except Product.DoesNotExist:
            raise ValidationError("Товар не найден")

    @staticmethod
    def get_cart_total(cart):
        """
        Получение общей стоимости корзины
        """
        return sum(item.product.price * item.quantity for item in cart.items.all())

    @staticmethod
    def clear_cart(cart):
        """
        Очистка корзины
        """
        return cart.items.all().delete()


class InventoryService:
    """Сервис для работы с инвентарем"""

    @staticmethod
    def update_stock(product_id, quantity_change):
        """
        Обновление остатков на складе
        """
        try:
            product = Product.objects.get(id=product_id)
            stock_balance, created = StockBalance.objects.get_or_create(
                product=product,
                defaults={'quantity': quantity_change}
            )

            if not created:
                stock_balance.quantity += quantity_change
                if stock_balance.quantity < 0:
                    raise ValidationError("Недостаточно товара на складе")
                stock_balance.save()

            return stock_balance
        except Product.DoesNotExist:
            raise ValidationError("Товар не найден")

    @staticmethod
    def get_low_stock_products(threshold=5):
        """
        Получение товаров с низким остатком
        """
        return StockBalance.objects.filter(quantity__lte=threshold)


class ProductService:
    """Сервис для работы с товарами"""

    @staticmethod
    def get_available_products():
        """
        Получение доступных товаров
        """
        return Product.objects.filter(is_active=True)

    @staticmethod
    def search_products(query):
        """
        Поиск товаров
        """
        return Product.objects.filter(
            name__icontains=query,
            is_active=True
        )