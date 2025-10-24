.PHONY: help build up down logs shell migrate collectstatic test clean

# Переменные
COMPOSE_FILE = docker-compose.yml
SERVICE_NAME = web

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Собрать Docker образы
	docker-compose -f $(COMPOSE_FILE) build

up: ## Запустить все сервисы
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## Остановить все сервисы
	docker-compose -f $(COMPOSE_FILE) down

logs: ## Показать логи
	docker-compose -f $(COMPOSE_FILE) logs -f

shell: ## Войти в контейнер Django
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) bash

migrate: ## Применить миграции
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python manage.py migrate

makemigrations: ## Создать миграции
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python manage.py makemigrations

collectstatic: ## Собрать статические файлы
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python manage.py collectstatic --noinput

createsuperuser: ## Создать суперпользователя
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python manage.py createsuperuser

loaddata: ## Загрузить фикстуры
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python manage.py loaddata booking/fixtures/site_content.json
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python manage.py loaddata booking/fixtures/tables.json
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python manage.py loaddata menu/fixtures/menu_data.json

test: ## Запустить тесты
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python manage.py test

clean: ## Очистить все контейнеры и образы
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f

restart: ## Перезапустить сервисы
	docker-compose -f $(COMPOSE_FILE) restart

status: ## Показать статус сервисов
	docker-compose -f $(COMPOSE_FILE) ps

# Команды для разработки
dev: ## Запустить в режиме разработки
	DEBUG=True docker-compose -f $(COMPOSE_FILE) up -d

dev-logs: ## Логи в режиме разработки
	DEBUG=True docker-compose -f $(COMPOSE_FILE) logs -f

# Команды для продакшена
prod: ## Запустить в продакшен режиме
	DEBUG=False docker-compose -f $(COMPOSE_FILE) up -d

prod-logs: ## Логи в продакшен режиме
	DEBUG=False docker-compose -f $(COMPOSE_FILE) logs -f
