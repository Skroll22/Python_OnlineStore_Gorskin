from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Product, Inventory, Cart, CartItem, Order, OrderItem, StockBalance

User = get_user_model()


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=100.00,
            is_active=True
        )

    def test_product_creation(self):
        """Тест создания товара"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, 100.00)
        self.assertTrue(self.product.is_active)
        self.assertIsNotNone(self.product.slug)

    def test_product_str_representation(self):
        """Тест строкового представления товара"""
        self.assertEqual(str(self.product), "Test Product")

    def test_product_get_absolute_url(self):
        """Тест получения абсолютного URL товара"""
        url = self.product.get_absolute_url()
        self.assertEqual(url, f'/store/{self.product.slug}/')


class InventoryModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=100.00
        )
        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity=50
        )

    def test_inventory_creation(self):
        """Тест создания складского запаса"""
        self.assertEqual(self.inventory.product, self.product)
        self.assertEqual(self.inventory.quantity, 50)

    def test_inventory_str_representation(self):
        """Тест строкового представления складского запаса"""
        expected_str = f"{self.product.name} - {self.inventory.quantity} шт."
        self.assertEqual(str(self.inventory), expected_str)


class StockBalanceModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=100.00
        )
        self.stock_balance = StockBalance.objects.create(
            product=self.product,
            quantity=30
        )

    def test_stock_balance_creation(self):
        """Тест создания остатка товара"""
        self.assertEqual(self.stock_balance.product, self.product)
        self.assertEqual(self.stock_balance.quantity, 30)

    def test_stock_balance_negative_quantity(self):
        """Тест: остаток не может быть отрицательным"""
        # Попытка создать отрицательный остаток должна вызвать ошибку
        with self.assertRaises(Exception):
            StockBalance.objects.create(
                product=self.product,
                quantity=-5
            )

    def test_stock_balance_str_representation(self):
        """Тест строкового представления остатка товара"""
        expected_str = f"{self.product.name} - {self.stock_balance.quantity} шт."
        self.assertEqual(str(self.stock_balance), expected_str)


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.product = Product.objects.create(
            name="Test Product",
            price=100.00
        )
        self.cart = Cart.objects.create(customer=self.user)

    def test_cart_creation(self):
        """Тест создания корзины"""
        self.assertEqual(self.cart.customer, self.user)
        self.assertIsNotNone(self.cart.created_at)

    def test_cart_total_price_empty(self):
        """Тест общей стоимости пустой корзины"""
        self.assertEqual(self.cart.total_price, 0)

    def test_cart_add_product(self):
        """Тест добавления товара в корзину"""
        cart_item = self.cart.add_product(self.product, quantity=2)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(self.cart.items.count(), 1)

    def test_cart_total_price_with_items(self):
        """Тест общей стоимости корзины с товарами"""
        self.cart.add_product(self.product, quantity=2)
        expected_total = self.product.price * 2
        self.assertEqual(self.cart.total_price, expected_total)


class StoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=100.00,
            is_active=True
        )

    def test_product_list_view(self):
        """Тест представления списка товаров"""
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product_list.html')
        self.assertContains(response, 'Test Product')

    def test_product_detail_view(self):
        """Тест представления деталей товара"""
        response = self.client.get(reverse('product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product_detail.html')
        self.assertContains(response, self.product.name)

    def test_home_page_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/home.html')