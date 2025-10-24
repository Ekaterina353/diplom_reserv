from django.core.management.base import BaseCommand

from booking.utils import send_telegram_message


class Command(BaseCommand):
    help = "Тестирование отправки сообщений в Telegram"

    def add_arguments(self, parser):
        parser.add_argument(
            "--message",
            type=str,
            default="Тестовое сообщение от Django приложения Žemaičiai",
            help="Текст сообщения для отправки",
        )

    def handle(self, *args, **options):
        message = options["message"]

        self.stdout.write("Отправка тестового сообщения в Telegram...")

        if send_telegram_message(message):
            self.stdout.write(self.style.SUCCESS("✅ Сообщение успешно отправлено!"))
        else:
            self.stdout.write(self.style.ERROR("❌ Ошибка при отправке сообщения"))
