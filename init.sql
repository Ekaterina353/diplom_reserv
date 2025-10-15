-- Инициализация базы данных для Django приложения
-- Этот скрипт выполняется при первом запуске PostgreSQL контейнера

-- Создаем расширения если их нет
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Устанавливаем кодировку
SET client_encoding = 'UTF8';

-- Создаем пользователя для приложения (если нужно)
-- CREATE USER resto_user WITH PASSWORD 'resto_password';
-- GRANT ALL PRIVILEGES ON DATABASE resto_reserve TO resto_user;

-- Комментарий для информации
COMMENT ON DATABASE resto_reserve IS 'База данных для системы бронирования ресторана Žemaičiai';
