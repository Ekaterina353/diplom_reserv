

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Получить Chat ID для Telegram бота"

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR("TELEGRAM_BOT_TOKEN не настроен в settings.py")
            )
            return

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"

        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            if not data.get("ok"):
                self.stdout.write(
                    self.style.ERROR(
                        f'Ошибка API: {data.get("description", "Неизвестная ошибка")}'
                    )
                )
                return

            updates = data.get("result", [])

            if not updates:
                self.stdout.write(
                    self.style.WARNING(
                        "Нет обновлений. Убедитесь, что:\n"
                        "1. Бот добавлен в чат/канал\n"
                        "2. В чат отправлено сообщение\n"
                        "3. Бот имеет права на чтение сообщений"
                    )
                )
                return

            self.stdout.write(self.style.SUCCESS("Найденные чаты:"))

            chat_ids = set()
            for update in updates:
                message = update.get("message", {})
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                chat_type = chat.get("type", "unknown")
                chat_title = chat.get("title", chat.get("first_name", "Unknown"))

                if chat_id:
                    chat_ids.add(chat_id)
                    self.stdout.write(
                        f"Chat ID: {chat_id} | Тип: {chat_type} | Название: {chat_title}"
                    )

            if chat_ids:
                self.stdout.write(
                    self.style.SUCCESS("\nДобавьте один из Chat ID в settings.py:\n")
                )
                for chat_id in chat_ids:
                    self.stdout.write(f'TELEGRAM_CHAT_ID = "{chat_id}"')

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при получении обновлений: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Неожиданная ошибка: {e}"))
