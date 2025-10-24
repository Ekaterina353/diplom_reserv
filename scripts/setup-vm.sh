#!/bin/bash

# 🖥️ Скрипт настройки виртуальной машины для деплоя
# Использование: ./scripts/setup-vm.sh

set -e

echo "🚀 Настройка виртуальной машины для деплоя Žemaičiai..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка прав администратора
if [[ $EUID -ne 0 ]]; then
   log_error "Этот скрипт должен быть запущен с правами администратора (sudo)"
   exit 1
fi

# Обновление системы
log_info "Обновление системы..."
apt-get update -y
apt-get upgrade -y

# Установка необходимых пакетов
log_info "Установка необходимых пакетов..."
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban \
    nginx \
    certbot \
    python3-certbot-nginx

# Установка Docker
log_info "Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $SUDO_USER
    log_success "Docker установлен"
else
    log_warning "Docker уже установлен"
fi

# Установка Docker Compose
log_info "Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    log_success "Docker Compose установлен"
else
    log_warning "Docker Compose уже установлен"
fi

# Настройка брандмауэра
log_info "Настройка брандмауэра..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp

# Настройка fail2ban
log_info "Настройка fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Создание пользователя для деплоя
log_info "Создание пользователя deploy..."
if ! id "deploy" &>/dev/null; then
    useradd -m -s /bin/bash deploy
    usermod -aG docker deploy
    log_success "Пользователь deploy создан"
else
    log_warning "Пользователь deploy уже существует"
fi

# Создание директории проекта
log_info "Создание директории проекта..."
mkdir -p /home/deploy/resto-reserve
chown -R deploy:deploy /home/deploy/resto-reserve

# Настройка Nginx
log_info "Настройка Nginx..."
cat > /etc/nginx/sites-available/dzukija << 'EOF'
server {
    listen 80;
    server_name _;
    
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
EOF

ln -sf /etc/nginx/sites-available/dzukija /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

# Настройка SSL (опционально)
log_info "Настройка SSL сертификата..."
read -p "Хотите настроить SSL сертификат? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Введите доменное имя: " domain_name
    if [ ! -z "$domain_name" ]; then
        sed -i "s/server_name _;/server_name $domain_name;/" /etc/nginx/sites-available/dzukija
        systemctl reload nginx
        certbot --nginx -d $domain_name --non-interactive --agree-tos --email admin@$domain_name
        log_success "SSL сертификат настроен для $domain_name"
    fi
fi

# Настройка автоматического обновления
log_info "Настройка автоматического обновления..."
apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# Создание systemd сервиса для автозапуска
log_info "Создание systemd сервиса..."
cat > /etc/systemd/system/Žemaičiai.service << 'EOF'
[Unit]
Description=Žemaičiai Restaurant Booking System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/deploy/resto-reserve
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=deploy
Group=deploy

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable Žemaičiai.service

# Настройка логирования
log_info "Настройка логирования..."
mkdir -p /var/log/dzukija
chown deploy:deploy /var/log/dzukija

# Создание скрипта для бэкапов
log_info "Создание скрипта для бэкапов..."
cat > /home/deploy/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап базы данных
docker-compose exec -T db pg_dump -U postgres resto_reserve > $BACKUP_DIR/db_backup_$DATE.sql

# Бэкап медиа файлов
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C /home/deploy/resto-reserve media/

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Бэкап завершен: $DATE"
EOF

chmod +x /home/deploy/backup.sh
chown deploy:deploy /home/deploy/backup.sh

# Добавление cron задачи для бэкапов
echo "0 2 * * * /home/deploy/backup.sh" | crontab -u deploy -

# Создание README для сервера
log_info "Создание документации..."
cat > /home/deploy/README.md << 'EOF'
# 🖥️ Žemaičiai Server Setup

## 📋 Информация о сервере

- **ОС**: Ubuntu Server
- **Пользователь**: deploy
- **Директория проекта**: /home/deploy/resto-reserve
- **Порт**: 80 (HTTP), 443 (HTTPS)

## 🚀 Команды управления

### Запуск/остановка приложения
```bash
# Запуск
sudo systemctl start Žemaičiai

# Остановка
sudo systemctl stop Žemaičiai

# Статус
sudo systemctl status Žemaičiai

# Перезапуск
sudo systemctl restart Žemaičiai
```

### Ручное управление Docker
```bash
cd /home/deploy/resto-reserve
docker-compose up -d
docker-compose down
docker-compose logs
```

### Бэкапы
```bash
# Ручной бэкап
/home/deploy/backup.sh

# Автоматический бэкап каждый день в 2:00
```

### Обновление системы
```bash
sudo apt-get update
sudo apt-get upgrade
```

## 🔧 Настройка

### Переменные окружения
Отредактируйте файл `/home/deploy/resto-reserve/.env`

### SSL сертификат
```bash
sudo certbot --nginx -d your-domain.com
```

## 📊 Мониторинг

### Логи
- Docker: `docker-compose logs`
- Nginx: `/var/log/nginx/`
- System: `journalctl -u Žemaičiai`

### Статус сервисов
```bash
sudo systemctl status nginx
sudo systemctl status docker
sudo systemctl status Žemaičiai
```
EOF

chown deploy:deploy /home/deploy/README.md

log_success "Настройка виртуальной машины завершена!"
log_info "Следующие шаги:"
log_info "1. Добавьте публичный SSH ключ в ~/.ssh/authorized_keys пользователя deploy"
log_info "2. Настройте .env файл в /home/deploy/resto-reserve/"
log_info "3. Добавьте секреты в GitHub Actions"
log_info "4. Запустите деплой через GitHub Actions"

echo ""
log_info "📋 Секреты для GitHub Actions:"
echo "DEPLOY_HOST: $(curl -s ifconfig.me)"
echo "DEPLOY_USER: deploy"
echo "DEPLOY_KEY: [приватный SSH ключ]"
