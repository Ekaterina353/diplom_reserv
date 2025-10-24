# Скрипт для запуска Django приложения в Docker

set -e

echo "🚀 Запуск Django приложения..."

# Ждем готовности базы данных
echo "⏳ Ожидание готовности базы данных..."
python manage.py wait_for_db

# Применяем миграции
echo "📦 Применение миграций..."
python manage.py migrate

# Собираем статические файлы
echo "📁 Сборка статических файлов..."
python manage.py collectstatic --noinput

# Создаем суперпользователя если нужно (только в development)
if [ "$DEBUG" = "True" ] && [ -z "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "👤 Создание суперпользователя..."
    python manage.py createsuperuser --username admin --email admin@example.com --noinput || true
fi

# Загружаем фикстуры если есть
if [ -f "booking/fixtures/site_content.json" ]; then
    echo "📋 Загрузка фикстур..."
    python manage.py loaddata booking/fixtures/site_content.json || true
fi

if [ -f "booking/fixtures/tables.json" ]; then
    echo "🪑 Загрузка данных о столиках..."
    python manage.py loaddata booking/fixtures/tables.json || true
fi

if [ -f "menu/fixtures/menu_data.json" ]; then
    echo "🍽️ Загрузка данных меню..."
    python manage.py loaddata menu/fixtures/menu_data.json || true
fi

# Запускаем сервер разработки (для простоты)
echo "🌟 Запуск Django сервера..."
exec python manage.py runserver 0.0.0.0:8000
