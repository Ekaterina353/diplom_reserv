import logging

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


def send_telegram_message(message, chat_id=None):
    """
    Отправляет сообщение в Telegram бот
    """

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не настроен в settings.py")
        return False

    # Используем chat_id из параметра или из настроек
    target_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
    if not target_chat_id:
        logger.error("TELEGRAM_CHAT_ID не настроен в settings.py")
        return False

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": target_chat_id,
        "text": message,
        "parse_mode": "HTML",  # Поддержка HTML разметки
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()

        result = response.json()
        if result.get("ok"):
            logger.info(f"Сообщение успешно отправлено в Telegram: {message[:50]}...")
            return True
        else:
            logger.error(
                f"Ошибка отправки в Telegram: {result.get('description', 'Неизвестная ошибка')}"
            )
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке в Telegram: {e}")
        return False


def format_contact_message(name, email, subject, message):
    """
    Форматирует сообщение из формы обратной связи для Telegram

    """
    formatted_message = f"""
<b>📧 НОВОЕ СООБЩЕНИЕ С САЙТА</b>

👤 <b>Имя:</b> {name}
📧 <b>Email:</b> {email}
📝 <b>Тема:</b> {subject}

💬 <b>Сообщение:</b>
{message}

---
<i>Отправлено с сайта Žemaičiai</i>
"""
    return formatted_message.strip()


def format_booking_notification(booking):
    """
    Форматирует уведомление о новом бронировании для Telegram

    """
    status_emoji = {
        "pending": "⏳",
        "confirmed": "✅",
        "paid": "💰",
        "completed": "🎉",
        "cancelled": "❌",
    }

    status_text = {
        "pending": "Ожидает предоплаты",
        "confirmed": "Подтверждено",
        "paid": "Предоплата внесена",
        "completed": "Завершено",
        "cancelled": "Отменено",
    }

    emoji = status_emoji.get(booking.status, "📋")
    status = status_text.get(booking.status, booking.status)

    preorder_info = ""
    if booking.has_preorder:
        preorder_info = f"""
🍽️ <b>Предзаказ:</b> {booking.preorder_total} ₽
💳 <b>Предоплата:</b> {booking.deposit_amount} ₽"""

        # Добавляем информацию о подтверждении
        if booking.deposit_confirmed_by:
            preorder_info += f"""
✅ <b>Подтверждено:</b> {booking.deposit_confirmed_by.get_full_name() or booking.deposit_confirmed_by.username}
⏰ <b>Дата:</b> {booking.deposit_confirmed_at.strftime('%d.%m.%Y %H:%M') if booking.deposit_confirmed_at else 'Не указана'}"""

        # Добавляем детали предзаказа
        if booking.preorder_items:
            preorder_info += "\n\n📋 <b>Детали заказа:</b>"
            for item in booking.preorder_items:
                quantity = item.get("quantity", 1)
                if quantity > 1:
                    preorder_info += (
                        f"\n• {item['name']} x{quantity} = {item['total']} ₽"
                    )
                else:
                    preorder_info += f"\n• {item['name']} = {item['price']} ₽"

    formatted_message = f"""
{emoji} <b>НОВОЕ БРОНИРОВАНИЕ</b>

👤 <b>Имя:</b> {booking.name}
📞 <b>Телефон:</b> {booking.phone}
📅 <b>Дата:</b> {booking.date.strftime('%d.%m.%Y')}
🕐 <b>Время:</b> {booking.time.strftime('%H:%M')}
🪑 <b>Столик:</b> №{booking.table.number} ({booking.table.seats} мест)
👥 <b>Гостей:</b> {booking.guests_count}
📊 <b>Статус:</b> {status}{preorder_info}

💬 <b>Комментарий:</b>
{booking.comments or 'Нет комментария'}

---
<i>ID бронирования: {booking.id}</i>
"""
    return formatted_message.strip()
