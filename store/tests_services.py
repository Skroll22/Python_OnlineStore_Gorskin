from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Product, Cart, Order, StockBalance
from .services import OrderService, CartService, InventoryService, ProductService

User = get_user_model()


class OrderServiceTest(TestCase):
    """Unit тесты для сервиса заказов"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.order = Order.objects.create(
            customer=self.user,
            total_amount=100.00,
            shipping_address="Initial Address",
            status='pending'
        )

    def test_process_order_success(self):
        """Тест успешной обработки заказа"""
        # Act
        processed_order = OrderService.process_order(
            self.order.id,
            "New Shipping Address"
        )

        # Assert
        self.assertEqual(processed_order.status, 'processing')
        self.assertEqual(processed_order.shipping_address, "New Shipping Address")

    def test_process_order_not_found(self):
        """Тест обработки несуществующего заказа"""
        # Act & Assert
        with self.assertRaises(ValidationError):
            OrderService.process_order(999, "Address")

    def test_get_orders_by_status(self):
        """Тест получения заказов по статусу"""
        # Arrange
        Order.objects.create(
            customer=self.user,
            total_amount=200.00,
            shipping_address="Address 2",
            status='processing'
        )

        # Act
        pending_orders = OrderService.get_orders_by_status('pending')
        processing_orders = OrderService.get_orders_by_status('processing')

        # Assert
        self.assertEqual(pending_orders.count(), 1)
        self.assertEqual(processing_orders.count(), 1)
        self.assertEqual(pending_orders.first().status, 'pending')

    def test_cancel_order_success(self):
        """Тест успешной отмены заказа"""
        # Act
        cancelled_order = OrderService.cancel_order(self.order.id)

        # Assert
        self.assertEqual(cancelled_order.status, 'cancelled')

    def test_cancel_order_not_found(self):
        """Тест отмены несуществующего заказа"""
        # Act & Assert
        with self.assertRaises(ValidationError):
            OrderService.cancel_order(999)


class CartServiceTest(TestCase):
    """Unit тесты для сервиса корзины"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.cart = Cart.objects.create(customer=self.user)
        self.product = Product.objects.create(
            name="Test Product",
            price=50.00,
            is_active=True
        )
        StockBalance.objects.create(product=self.product, quantity=10)

    def test_add_to_cart_success(self):
        """Тест успешного добавления товара в корзину"""
        # Act
        cart_item = CartService.add_to_cart(self.cart, self.product.id, 2)

        # Assert
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(self.cart.items.count(), 1)

    def test_add_to_cart_insufficient_stock(self):
        """Тест добавления товара при недостаточном количестве на складе"""
        # Act & Assert
        with self.assertRaises(ValidationError):
            CartService.add_to_cart(self.cart, self.product.id, 20)

    def test_add_to_cart_product_not_found(self):
        """Тест добавления несуществующего товара"""
        # Act & Assert
        with self.assertRaises(ValidationError):
            CartService.add_to_cart(self.cart, 999, 1)

    def test_add_to_cart_inactive_product(self):
        """Тест добавления неактивного товара"""
        # Arrange
        inactive_product = Product.objects.create(
            name="Inactive Product",
            price=30.00,
            is_active=False
        )

        # Act & Assert
        with self.assertRaises(ValidationError):
            CartService.add_to_cart(self.cart, inactive_product.id, 1)

    def test_get_cart_total(self):
        """Тест расчета общей стоимости корзины"""
        # Arrange
        CartService.add_to_cart(self.cart, self.product.id, 2)
        product2 = Product.objects.create(name="Product 2", price=25.00, is_active=True)
        StockBalance.objects.create(product=product2, quantity=5)
        CartService.add_to_cart(self.cart, product2.id, 1)

        # Act
        total = CartService.get_cart_total(self.cart)

        # Assert
        expected_total = (50.00 * 2) + (25.00 * 1)
        self.assertEqual(total, expected_total)

    def test_clear_cart(self):
        """Тест очистки корзины"""
        # Arrange
        CartService.add_to_cart(self.cart, self.product.id, 1)

        # Act
        deleted_count = CartService.clear_cart(self.cart)

        # Assert
        self.assertEqual(deleted_count[0], 1)
        self.assertEqual(self.cart.items.count(), 0)


class InventoryServiceTest(TestCase):
    """Unit тесты для сервиса инвентаря"""

    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            price=100.00
        )

    def test_update_stock_add_quantity(self):
        """Тест увеличения остатка на складе"""
        # Act
        stock = InventoryService.update_stock(self.product.id, 10)

        # Assert
        self.assertEqual(stock.quantity, 10)

    def test_update_stock_existing_balance(self):
        """Тест обновления существующего остатка"""
        # Arrange
        InventoryService.update_stock(self.product.id, 10)

        # Act
        stock = InventoryService.update_stock(self.product.id, 5)

        # Assert
        self.assertEqual(stock.quantity, 15)

    def test_update_stock_insufficient_quantity(self):
        """Тест уменьшения остатка ниже нуля"""
        # Arrange
        InventoryService.update_stock(self.product.id, 5)

        # Act & Assert
        with self.assertRaises(ValidationError):
            InventoryService.update_stock(self.product.id, -10)

    def test_update_stock_product_not_found(self):
        """Тест обновления остатка несуществующего товара"""
        # Act & Assert
        with self.assertRaises(ValidationError):
            InventoryService.update_stock(999, 10)

    def test_get_low_stock_products(self):
        """Тест получения товаров с низким остатком"""
        # Arrange
        product_low = Product.objects.create(name="Low Stock Product", price=50.00)
        product_ok = Product.objects.create(name="OK Stock Product", price=60.00)

        InventoryService.update_stock(product_low.id, 3)  # Низкий остаток
        InventoryService.update_stock(product_ok.id, 10)  # Нормальный остаток

        # Act
        low_stock_products = InventoryService.get_low_stock_products(threshold=5)

        # Assert
        self.assertEqual(low_stock_products.count(), 1)
        self.assertEqual(low_stock_products.first().product, product_low)


class ProductServiceTest(TestCase):
    """Unit тесты для сервиса товаров"""

    def setUp(self):
        self.active_product = Product.objects.create(
            name="Active Product",
            price=100.00,
            is_active=True
        )
        self.inactive_product = Product.objects.create(
            name="Inactive Product",
            price=200.00,
            is_active=False
        )

    def test_get_available_products(self):
        """Тест получения доступных товаров"""
        # Act
        available_products = ProductService.get_available_products()

        # Assert
        self.assertEqual(available_products.count(), 1)
        self.assertEqual(available_products.first(), self.active_product)
        self.assertNotIn(self.inactive_product, available_products)

    def test_search_products(self):
        """Тест поиска товаров"""

        test_product1 = Product.objects.create(
            name="Test Product One",
            price=150.00,
            is_active=True
        )
        test_product2 = Product.objects.create(
            name="Another Test Product",
            price=160.00,
            is_active=True
        )

        # Act
        search_results = ProductService.search_products("test")

        # Assert
        self.assertEqual(search_results.count(), 2)

        found_products = list(search_results)
        self.assertIn(test_product1, found_products)
        self.assertIn(test_product2, found_products)

        self.assertNotIn(self.inactive_product, found_products)

    def test_search_products_no_results(self):
        """Тест поиска товаров без результатов"""
        # Act
        search_results = ProductService.search_products("nonexistent")

        # Assert
        self.assertEqual(search_results.count(), 0)