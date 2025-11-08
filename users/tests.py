from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='John',
            surname='Doe',
            phone='+1234567890',
            address='Test Address'
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.surname, 'Doe')
        self.assertEqual(self.user.phone, '+1234567890')
        self.assertEqual(self.user.address, 'Test Address')

    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        expected_str = f" John (testuser)"
        self.assertEqual(str(self.user), expected_str)

    def test_user_required_fields(self):
        """Тест обязательных полей пользователя"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='',
                password='testpass123'
            )

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_register_view(self):
        """Тест представления регистрации"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_login_view(self):
        """Тест представления входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

        # Тест POST запроса
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа

    def test_logout_view_authenticated(self):
        """Тест представления выхода для аутентифицированного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/logout.html')