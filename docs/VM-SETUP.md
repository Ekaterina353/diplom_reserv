# 🖥️ Настройка виртуальной машины test2 для деплоя

## 📋 Информация о VM

- **Название**: `test2`
- **IP адрес**: `89.169.160.116`
- **Пользователь**: `deploy`
- **Директория проекта**: `/home/deploy/resto-reserve`
- **Порт**: 80 (HTTP), 443 (HTTPS)

## 🚀 Быстрая настройка

### 1. Подключение к VM

```bash
# Подключение как root (или ваш пользователь)
ssh katja@89.169.160.116

# Или если у вас есть другой пользователь
ssh your-user@89.169.160.116
```

### 2. Автоматическая настройка

```bash
# Клонируйте репозиторий локально
git clone https://github.com/your-username/resto-reserve.git
cd resto-reserve

# Запустите скрипт настройки
chmod +x scripts/setup-vm-remote.sh
./scripts/setup-vm-remote.sh
```

### 3. Добавление SSH ключа

```bash
# Добавьте ваш SSH ключ на VM
chmod +x scripts/add-ssh-key.sh
./scripts/add-ssh-key.sh
```

## 🔧 Ручная настройка

### 1. Обновление системы

```bash
sudo apt-get update -y
sudo apt-get upgrade -y
```

### 2. Установка Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Создание пользователя deploy

```bash
# Создание пользователя
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Создание директории проекта
sudo mkdir -p /home/deploy/resto-reserve
sudo chown -R deploy:deploy /home/deploy/resto-reserve
```

### 4. Настройка SSH

```bash
# Создание директории .ssh
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh

# Добавление публичного ключа
sudo nano /home/deploy/.ssh/authorized_keys
# Вставьте содержимое вашего публичного ключа

# Установка прав
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

### 5. Настройка брандмауэра

```bash
# Включение UFW
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 6. Настройка Nginx

```bash
# Установка Nginx
sudo apt-get install -y nginx

# Создание конфигурации
sudo nano /etc/nginx/sites-available/dzukija
```

Содержимое конфигурации Nginx:
```nginx
server {
    listen 80;
    server_name 89.169.160.116;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/deploy/resto-reserve/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/deploy/resto-reserve/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

```bash
# Активация конфигурации
sudo ln -sf /etc/nginx/sites-available/dzukija /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```

## 🔑 Настройка GitHub Actions

### Секреты для добавления в GitHub:

1. **DEPLOY_HOST**: `89.169.160.116`
2. **DEPLOY_USER**: `deploy`
3. **DEPLOY_KEY**: [приватный SSH ключ]

### Получение приватного SSH ключа:

```bash
# На Windows
type C:\Users\Екатерина\.ssh\ssh-key-1759945161226

# Скопируйте весь вывод (включая BEGIN и END строки)
```

## 🧪 Тестирование

### 1. Проверка подключения

```bash
# Тест SSH подключения
ssh deploy@130.193.34.169

# Тест Docker
docker --version
docker-compose --version
```

### 2. Ручной деплой

```bash
# Подключение к VM
ssh deploy@89.169.160.116

# Клонирование репозитория
cd /home/deploy
git clone https://github.com/your-username/resto-reserve.git
cd resto-reserve

# Создание .env файла
cp env.example .env
nano .env  # Настройте переменные

# Запуск приложения
docker-compose up -d
```

### 3. Проверка работоспособности

```bash
# Проверка контейнеров
docker-compose ps

# Проверка логов
docker-compose logs web

# Проверка доступности
curl http://89.169.160.116/health/
```

## 📊 Мониторинг

### Команды для мониторинга:

```bash
# Статус сервисов
sudo systemctl status nginx
sudo systemctl status docker

# Логи
sudo journalctl -u nginx
docker-compose logs -f

# Использование ресурсов
htop
df -h
free -h
```

### Автоматические бэкапы:

```bash
# Ручной бэкап
/home/deploy/backup.sh

# Проверка cron задач
crontab -l -u deploy
```

## 🔒 Безопасность

### Рекомендации:

1. **Регулярные обновления**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

2. **Мониторинг логов**:
   ```bash
   sudo tail -f /var/log/auth.log
   sudo tail -f /var/log/nginx/access.log
   ```

3. **Проверка открытых портов**:
   ```bash
   sudo netstat -tlnp
   sudo ufw status
   ```

4. **SSL сертификат** (опционально):
   ```bash
   sudo apt-get install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## 🐛 Устранение неполадок

### Частые проблемы:

1. **Ошибка подключения SSH**:
   ```bash
   # Проверьте права на ключи
   chmod 600 ~/.ssh/id_rsa
   chmod 644 ~/.ssh/id_rsa.pub
   ```

2. **Docker не запускается**:
   ```bash
   # Перезапуск Docker
   sudo systemctl restart docker
   sudo usermod -aG docker $USER
   ```

3. **Nginx не работает**:
   ```bash
   # Проверка конфигурации
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **Приложение недоступно**:
   ```bash
   # Проверка контейнеров
   docker-compose ps
   docker-compose logs web
   
   # Проверка портов
   sudo netstat -tlnp | grep 8000
   ```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs`
2. Проверьте статус сервисов: `sudo systemctl status`
3. Создайте issue в GitHub репозитории
4. Обратитесь к документации Docker и Nginx

## 🏷️ Информация о сервере

- **Название**: test2
- **IP**: 89.169.160.116
- **Назначение**: Продакшн сервер для Žemaičiai
- **ОС**: Ubuntu Server
- **Статус**: Активен
