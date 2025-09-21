from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=True, label='Имя')
    surname = forms.CharField(required=True, label='Фамилия')
    phone = forms.CharField(required=False, label='Телефон')
    address = forms.CharField(required=False, label='Адрес', widget=forms.Textarea)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'surname', 'patronymic', 'phone', 'address', 'birth_date', 'password1', 'password2')