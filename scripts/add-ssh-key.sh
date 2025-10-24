#!/bin/bash

# 🔑 Скрипт для добавления SSH ключа на VM test2
# Использование: ./scripts/add-ssh-key.sh

VM_NAME="test2"
VM_IP="89.169.160.116"
VM_USER="root"  # или ваш пользователь
SSH_KEY_PATH="C:\Users\Екатерина\.ssh\Žemaičiai_deploy.pub"

echo "🔑 Добавление SSH ключа на VM $VM_NAME ($VM_IP)..."

# Проверка существования публичного ключа
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "❌ Публичный ключ не найден: $SSH_KEY_PATH"
    exit 1
fi

# Копирование публичного ключа на VM
echo "📤 Копирование публичного ключа..."
scp "$SSH_KEY_PATH" $VM_USER@$VM_IP:/tmp/deploy_key.pub

# Добавление ключа в authorized_keys
echo "🔧 Добавление ключа в authorized_keys..."
ssh $VM_USER@$VM_IP << 'EOF'
    # Создание директории .ssh для пользователя deploy
    mkdir -p /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
    
    # Добавление публичного ключа
    cat /tmp/deploy_key.pub >> /home/deploy/.ssh/authorized_keys
    chmod 600 /home/deploy/.ssh/authorized_keys
    
    # Установка правильных прав
    chown -R deploy:deploy /home/deploy/.ssh
    
    # Очистка временного файла
    rm /tmp/deploy_key.pub
    
    echo "✅ SSH ключ успешно добавлен для пользователя deploy"
EOF

echo "✅ SSH ключ добавлен на VM $VM_NAME!"
echo ""
echo "🧪 Тестирование подключения..."
ssh -i "C:\Users\Екатерина\.ssh\_deploy.pub" deploy@$VM_IP "echo '✅ Подключение по SSH к $VM_NAME работает!'"
