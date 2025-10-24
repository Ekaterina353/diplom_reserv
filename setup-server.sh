#!/bin/bash

# Скрипт для настройки сервера и добавления SSH ключа
# Запускать на сервере 130.193.34.169

echo "🔧 Настройка сервера для деплоя..."

# Создать пользователя deploy, если его нет
if ! id "deploy" &>/dev/null; then
    echo "👤 Создаю пользователя deploy..."
    sudo useradd -m -s /bin/bash deploy
    sudo usermod -aG sudo deploy
    echo "deploy:deploy123" | sudo chpasswd
fi

# Создать папку .ssh для пользователя deploy
sudo mkdir -p /home/deploy/.ssh
sudo chown deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh

# Добавить публичный ключ в authorized_keys
echo "🔑 Добавляю SSH ключ..."
sudo tee -a /home/deploy/.ssh/authorized_keys > /dev/null << 'EOF'
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDC8A2GtvDkW1VHDd97NSAjtlz5ckgwLUCdXE8KQqtJCjQ9xinEZmB9L2LnaXafMKaIiysygUBiQIHYTQc7Y5HcSr1P+hm2vUhtIy5nHGqmqhjihC4Q5IlIXojZcAnYBQZ6A21VP9zfFNh1164ioLp/ZE4uB0BDPHx//nI3d7C0580pnwJrrSAIPxAwLZTyv8l6DmA/s+sbeuYat/a5tjfwGmU6NHUo+6epD5ppZZnK2zCT5RjEHQcRhUdq/CFT4Hos0hLGV8Qzw9vJoX7ZB+YGowZCiWZaysXT03u+TQHPFsbJ4OeFRVDg2kHeJ8Q/sJKU+vA/OstXLsEsOgU6pkAlgdeidituygfFuu3wVEhqTyG8MI5pz+KCIxIDQjSCxLHX384xVvRAbPJ/6q0BiE/70ZC6dofIJ7Bvaae1FfARS1tRbgxrwLfu6ADfukRXZECj0hFIxBA2mFs4KpJx+SXHhqYLxuAm+Ead5gVetNkm0Rheg07yFI3894MRSluHAu/nWAFMDjdvH4GNEzHg/pp3Z1lY7YiefxUHvnZu/Hy93EbG+Qway+urtEP+WBZz6MaDfnOkNvzjkN0nh1VQUYlEhjTuBK4i8ihvUCigq4Sga1YFqJq4/O4mxnLNr0qxPSK8mHRGVDrHeZgn3QhviUlHd79R8gfW804sUP7e1SYTNw== kcenka@DESKTOP-GUFNDUR
EOF

# Установить правильные права
sudo chown deploy:deploy /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys

# Установить Docker, если его нет
if ! command -v docker &> /dev/null; then
    echo "🐳 Устанавливаю Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker deploy
    rm get-docker.sh
fi

# Установить Docker Compose, если его нет
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Устанавливаю Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Создать папку для проекта
sudo mkdir -p /home/deploy/resto-reserve
sudo chown deploy:deploy /home/deploy/resto-reserve

echo "✅ Настройка сервера завершена!"
echo "📝 Теперь можно использовать следующие данные для деплоя:"
echo "   - DEPLOY_HOST: 130.193.34.169"
echo "   - DEPLOY_USER: deploy"
echo "   - SSH_PORT: 22"
echo "   - DEPLOY_KEY: (приватный ключ, который мы создали)"
