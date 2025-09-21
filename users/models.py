from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    username = models.CharField('Логин', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    surname = models.CharField('Фамилия', max_length=150)
    patronymic = models.CharField('Отчество', max_length=150, blank=True)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    address = models.TextField('Адрес', blank=True)
    avatar = models.ImageField('Аватар', upload_to='users/avatars/', blank=True, null=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"