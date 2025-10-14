#!/bin/bash

# 🖥️ Скрипт для удаленной настройки VM test2 (130.193.34.169)
# Использование: ./scripts/setup-vm-remote.sh

VM_NAME="test2"
VM_IP="130.193.34.169"
VM_USER="root"  # или ваш пользователь

echo "🚀 Настройка виртуальной машины $VM_NAME ($VM_IP)..."

# Проверка подключения
echo "🔍 Проверка подключения к VM..."
if ! ping -c 1 $VM_IP &> /dev/null; then
    echo "❌ Не удается подключиться к $VM_IP"
    exit 1
fi

echo "✅ Подключение к VM $VM_NAME установлено"

# Копирование скрипта настройки на VM
echo "📤 Копирование скрипта настройки..."
scp scripts/setup-vm.sh $VM_USER@$VM_IP:/tmp/setup-vm.sh

# Выполнение настройки на VM
echo "🔧 Запуск настройки на VM $VM_NAME..."
ssh $VM_USER@$VM_IP << 'EOF'
    chmod +x /tmp/setup-vm.sh
    sudo /tmp/setup-vm.sh
EOF

echo "✅ Настройка VM $VM_NAME завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Добавьте публичный SSH ключ в ~/.ssh/authorized_keys пользователя deploy"
echo "2. Настройте .env файл в /home/deploy/resto-reserve/"
echo "3. Добавьте секреты в GitHub Actions:"
echo "   - DEPLOY_HOST: 130.193.34.169"
echo "   - DEPLOY_USER: deploy"
echo "   - DEPLOY_KEY: [приватный SSH ключ]"
echo ""
echo "🌐 После настройки приложение будет доступно по адресу:"
echo "   http://130.193.34.169"
