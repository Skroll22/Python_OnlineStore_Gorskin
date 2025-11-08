FROM python:3.11

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=MyOnlineStore.settings

# Создание и установка рабочего каталога
WORKDIR /app

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копирование всего проекта
COPY . /app/

# Создание статических файлов
RUN python manage.py collectstatic --no-input

# Открытие порта
EXPOSE 8000

# Запуск приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]