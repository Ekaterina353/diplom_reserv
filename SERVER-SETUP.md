# 🔧 Настройка сервера для деплоя

## 📋 Информация о сервере

- **IP адрес**: 89.169.160.116
- **Название**: test2
- **Пользователь для деплоя**: test2

## 🚀 Пошаговая настройка

### 1. Подключение к серверу

```bash
ssh root@89.169.160.116
```

### 2. Создание пользователя test2 (если не существует)

```bash
# Проверить, существует ли пользователь test2
id test2

# Если пользователь не существует, создать его
if ! id test2 &>/dev/null; then
    sudo useradd -m -s /bin/bash test2
    sudo usermod -aG sudo test2
    echo "test2:test2123" | sudo chpasswd
fi
```

### 3. Настройка SSH для пользователя test2

```bash
# Создать папку .ssh
sudo mkdir -p /home/test2/.ssh
sudo chown test2:test2 /home/test2/.ssh
sudo chmod 700 /home/test2/.ssh

# Создать файл authorized_keys
sudo touch /home/test2/.ssh/authorized_keys
sudo chown test2:test2 /home/test2/.ssh/authorized_keys
sudo chmod 600 /home/test2/.ssh/authorized_keys
```

### 4. Добавить публичный ключ

```bash
# Открыть файл для редактирования
sudo nano /home/test2/.ssh/authorized_keys
```

**Вставить следующий публичный ключ:**

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDG/aW6NhAtvkbYHO6FkZ6TMx5njyX17YXGq0dBsIgzFm4P+o6eqAUaJGBRnj666GHMyGF/vAAz5HCWKPLBK9rLgjGbvTfjlYsiQmKwQ/l+lDakcE1+vXNUGr+bAMiU9vQNgjxMQqSA9iCZRmwC6fWwSBGA2WUgu8k6EXiLN/lhysTDcEtpEiVfOSps2QIX71Ku153g5Z0w6u9y0hsPLwOjS81ZB7P4cSlclwbi21ep83TA2Tqx78DoUqu0+pK82APvaVtD/qbzuHK2mTXOpLRdpl4Ljg6IT0CHz9Fp44hZcK+fBk5SrEsUNfUaSJXc7K7fVWhDtGSeF37dEMfap7NzwPy32gPteHSrDIK8Hixy8x4hS5pTh3Dp/YXhwUPyXsobBpZwoATlvkTS8U9gdgK0mVqhzHMSjV1xTd3LY3VyzzQR5YTR7hMwnsRqPPg21uiUBCz6ho52KwMTKflllLp3BBie2WLK9iRfeTaY+SIKXXCi0OB5gWAkPN+ziX/mQkEtjuHJ3nOUnRjSASzD7crYLrdnJefcZDcuAk2tOTGad6UkPyX8aWUIiVJ1vFqEvGQd2D/2DBJq8jUnQhqAk3KjzWwZLHuoeDJLCKCuOEVsiLDOIbcsuIa6pEevkHbUdNZ8K1j/Eb5KVmxfJXDoijWB3OCkCKpYZaasqPQk0+vBwQ== kcenka@DESKTOP-GUFNDUR
```

### 5. Установка Docker

```bash
# Обновить систему
sudo apt-get update -y
sudo apt-get upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавить пользователя test2 в группу docker
sudo usermod -aG docker test2

# Удалить скрипт установки
rm get-docker.sh
```

### 6. Установка Docker Compose

```bash
# Скачать Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Сделать исполняемым
sudo chmod +x /usr/local/bin/docker-compose

# Проверить установку
docker-compose --version
```

### 7. Создание папки проекта

```bash
# Создать папку для проекта
sudo mkdir -p /home/test2/resto-reserve
sudo chown test2:test2 /home/test2/resto-reserve
```

### 8. Тестирование подключения

```bash
# Переключиться на пользователя test2
sudo su - test2

# Проверить, что SSH работает
ssh test2@localhost

# Выйти из пользователя test2
exit
```

### 9. Настройка брандмауэра

```bash
# Включить UFW
sudo ufw --force enable

# Настроить правила
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Проверить статус
sudo ufw status
```

## 🔑 Проверка настройки

### Тест SSH подключения с вашего компьютера:

```bash
ssh test2@89.169.160.116
```

Если подключение успешно, вы должны увидеть приглашение командной строки.

### Тест Docker:

```bash
# Подключиться к серверу
ssh test2@89.169.160.116

# Проверить Docker
docker --version
docker-compose --version
```

## 📝 Секреты для GitHub Actions

После успешной настройки сервера добавьте следующие секреты в GitHub:

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Имя секрета          | Значение                                         |
|----------------------|--------------------------------------------------|
| `DEPLOY_HOST`        | `89.169.160.116`                                 |
| `DEPLOY_USER`        | `test2`                                          |
| `SSH_PORT`           | `22`                                             |
| `DEPLOY_KEY`         | [Приватный ключ из файла]                        |
| `DEBUG`              | `False`                                          |
| `SECRET_KEY`         | [Ваш Django SECRET_KEY]                          |
| `DB_PASSWORD`        | `261110170712`                                   |
| `TELEGRAM_BOT_TOKEN` | `7872717484:AAEkeg9mR0tUL5qYKTSNc4uymWtdhfpvZQM` |
| `TELEGRAM_CHAT_ID`   | `311492733`                                      |

## 🚨 Устранение неполадок

### Если SSH не подключается:

1. Проверьте, что публичный ключ добавлен правильно
2. Проверьте права доступа к файлам:
   ```bash
   ls -la /home/test2/.ssh/
   ```
3. Проверьте логи SSH:
   ```bash
   sudo tail -f /var/log/auth.log
   ```

### Если Docker не работает:

1. Проверьте, что Docker установлен:
   ```bash
   docker --version
   ```
2. Проверьте, что пользователь в группе docker:
   ```bash
   groups test2
   ```

### Если деплой не работает:

1. Проверьте секреты в GitHub
2. Проверьте логи GitHub Actions
3. Проверьте подключение к серверу вручную

## ✅ Готово!

После выполнения всех шагов ваш сервер будет готов к автоматическому деплою через GitHub Actions.
