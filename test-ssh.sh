#!/bin/bash

# Скрипт для тестирования SSH подключения к серверу

echo "🔍 Тестирование SSH подключения к серверу..."

# Проверка наличия SSH ключа
if [ ! -f ~/.ssh/deploy_key ]; then
    echo "❌ SSH ключ не найден: ~/.ssh/deploy_key"
    echo "Создайте ключ командой: ssh-keygen -t rsa -b 4096 -f ~/.ssh/deploy_key -N ''"
    exit 1
fi

echo "✅ SSH ключ найден"

# Тест подключения с подробным выводом
echo "🔗 Тестирую подключение к test2@130.193.34.169..."
ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no -o ConnectTimeout=10 -v test2@130.193.34.169 "echo 'SSH подключение успешно!' && whoami && pwd"

if [ $? -eq 0 ]; then
    echo "✅ SSH подключение работает!"
else
    echo "❌ SSH подключение не работает"
    echo ""
    echo "🔧 Возможные решения:"
    echo "1. Проверьте, что сервер доступен: ping 130.193.34.169"
    echo "2. Проверьте, что пользователь deploy создан на сервере"
    echo "3. Проверьте, что публичный ключ добавлен в ~/.ssh/authorized_keys"
    echo "4. Проверьте права доступа к файлам SSH"
    echo ""
    echo "📋 Выполните настройку сервера по инструкции в SERVER-SETUP.md"
fi
