from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from menu.models import MenuItem

from .forms import BookingForm, ContactForm
from .models import Booking, Table, TeamMember
from .utils import (
    format_booking_notification,
    format_contact_message,
    send_telegram_message,
)


def home(request):
    """Главная страница"""
    context = {
        "services": [
            "Традиционная литовская кухня",
            "Бронирование столиков",
            "Кейтеринговые услуги",
            "Проведение тематических вечеров",
        ],
        "contact_info": {
            "address": "ул. Красная, 123, Краснодар",
            "phone": "+7 (988) 123-45-67",
            "email": "info@dzukija.ru",
            "hours": "Ежедневно с 10:00 до 22:00",
        },
    }
    return render(request, "booking/home.html", context)


def about(request):
    """Страница о ресторане"""
    team_members = TeamMember.objects.all()
    context = {
        "team_members": team_members,
        "history": "Ресторан Žemaičiai был основан в 2018 году с целью приблизить жителей Краснодара к богатой культуре Литвы.",
        "mission": "Познакомить российскую публику с разнообразием литовской кухни и культуры.",
        "values": [
            "Сохранение традиций",
            "Качество ингредиентов",
            "Гостеприимство",
            "Экологичность",
        ],
    }
    return render(request, "booking/about.html", context)


def booking_page(request):
    """Страница бронирования"""
    # Получаем информацию о выбранном блюде
    selected_item = None
    if request.GET.get("item") and MenuItem:
        try:
            selected_item = MenuItem.objects.get(
                id=request.GET.get("item"), is_available=True
            )
        except MenuItem.DoesNotExist:
            pass

    if request.method == "POST":
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)

            # Получаем выбранный столик
            table_id = form.cleaned_data.get("table")
            if table_id:
                try:
                    table = Table.objects.get(id=int(table_id))
                    booking.table = table
                except (Table.DoesNotExist, ValueError):
                    messages.error(request, "Выбранный столик недоступен.")
                    return render(
                        request,
                        "booking/booking.html",
                        {"form": form, "selected_item": selected_item},
                    )

            if request.user.is_authenticated:
                booking.user = request.user

            # Устанавливаем данные предзаказа и предоплаты
            booking.preorder_total = form.cleaned_data.get("preorder_total", 0)
            booking.preorder_items = form.cleaned_data.get("preorder_items", [])
            booking.has_preorder = len(form.cleaned_data.get("preorder_items", [])) > 0
            booking.deposit_amount = form.cleaned_data.get("deposit_amount", 0)

            # Устанавливаем статус в зависимости от наличия предзаказа
            if booking.has_preorder:
                booking.status = "pending"  # Требуется предоплата
            else:
                booking.status = "confirmed"  # Бронирование сразу подтверждено

            # Добавляем информацию о выбранном блюде в комментарий
            if selected_item:
                original_comments = booking.comments or ""
                item_info = f"\n\nВыбранное блюдо: {selected_item.name} - {selected_item.price} ₽"
                booking.comments = original_comments + item_info

            # Добавляем информацию о предзаказе в комментарий
            if booking.has_preorder:
                items_info = "\n\nПредзаказанные блюда:"
                for item in booking.preorder_items:
                    quantity = item.get("quantity", 1)
                    if quantity > 1:
                        items_info += f"\n- {item['name']} x{quantity} - {item['price']} ₽ за шт. = {item['total']} ₽"
                    else:
                        items_info += f"\n- {item['name']} - {item['price']} ₽"
                items_info += (
                    f"\n\nОбщая стоимость предзаказа: {booking.preorder_total} ₽"
                )
                items_info += f"\nСумма предоплаты: {booking.deposit_amount} ₽"

                original_comments = booking.comments or ""
                booking.comments = original_comments + items_info

            booking.save()

            # Отправляем уведомление о новом бронировании в Telegram
            telegram_message = format_booking_notification(booking)
            send_telegram_message(telegram_message)

            if booking.has_preorder:
                messages.success(
                    request,
                    "Ваш столик забронирован! Требуется внести предоплату для подтверждения предзаказа.",
                )
            else:
                messages.success(request, "Ваш столик успешно забронирован!")

            return redirect("booking:booking_success")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = BookingForm(user=request.user)

    # Получаем все столики
    tables = Table.objects.all()

    context = {
        "form": form,
        "tables": tables,
        "selected_item": selected_item,
    }
    return render(request, "booking/booking.html", context)


def contact(request):
    """Обратная связь"""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Отправляем сообщение в Telegram
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            # Форматируем сообщение для Telegram
            telegram_message = format_contact_message(name, email, subject, message)

            # Отправляем в Telegram
            if send_telegram_message(telegram_message):
                messages.success(
                    request,
                    "Сообщение отправлено! Мы свяжемся с вами в ближайшее время.",
                )
            else:
                messages.warning(
                    request,
                    "Сообщение сохранено, но возникли проблемы с отправкой уведомления.",
                )

            return redirect("booking:home")
    else:
        form = ContactForm()

    return render(request, "booking/contact.html", {"form": form})


def booking_success(request):
    """Страница успешного бронирования"""
    # Получаем последнее бронирование пользователя
    if request.user.is_authenticated:
        try:
            booking = Booking.objects.filter(user=request.user).latest("created_at")
        except Booking.DoesNotExist:
            booking = None
    else:
        booking = None

    context = {
        "booking": booking,
    }
    return render(request, "booking/booking_success.html", context)


@login_required
def booking_detail(request, booking_id):
    """Детальный просмотр бронирования"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, "booking/booking_detail.html", {"booking": booking})


@staff_member_required
@require_POST
def confirm_payment(request, booking_id):
    """Подтверждение внесения предоплаты администратором"""
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status == "pending" and booking.has_preorder:
        booking.status = "paid"
        booking.deposit_paid = True
        booking.deposit_paid_at = timezone.now()
        booking.deposit_confirmed_by = request.user
        booking.deposit_confirmed_at = timezone.now()
        booking.save()

        # Отправляем уведомление в Telegram о подтверждении предоплаты
        telegram_message = f"""
💰 <b>ПРЕДОПЛАТА ПОДТВЕРЖДЕНА</b>

👤 <b>Клиент:</b> {booking.name}
📞 <b>Телефон:</b> {booking.phone}
📅 <b>Дата:</b> {booking.date.strftime('%d.%m.%Y')}
🕐 <b>Время:</b> {booking.time.strftime('%H:%M')}
🪑 <b>Столик:</b> №{booking.table.number}
💳 <b>Сумма предоплаты:</b> {booking.deposit_amount} ₽

👨‍💼 <b>Подтвердил:</b> {request.user.get_full_name() or request.user.username}
⏰ <b>Время подтверждения:</b> {timezone.now().strftime('%d.%m.%Y %H:%M')}

---
<i>ID бронирования: {booking.id}</i>
"""
        send_telegram_message(telegram_message)

        messages.success(
            request, f"Предоплата для бронирования {booking.name} подтверждена!"
        )
    else:
        messages.error(
            request, "Невозможно подтвердить предоплату для данного бронирования."
        )

    return redirect("admin:booking_booking_changelist")


@login_required
@require_POST
def cancel_booking(request, booking_id):
    """Отмена бронирования (только для бронирований без предзаказа)"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.can_be_cancelled:
        booking.status = "cancelled"
        booking.save()
        messages.success(request, "Бронирование успешно отменено.")
    else:
        messages.error(request, "Это бронирование нельзя отменить.")

    return redirect("user:my_bookings")


@require_POST
def check_table_availability(request):
    """AJAX проверка доступности столика"""
    date = request.POST.get("date")
    time = request.POST.get("time")

    if date and time:
        try:
            booking_date = datetime.strptime(date, "%Y-%m-%d").date()
            booking_time = datetime.strptime(time, "%H:%M").time()

            # Проверяем, есть ли уже брони на это время
            existing_bookings = Booking.objects.filter(
                date=booking_date,
                time=booking_time,
                status__in=["pending", "paid", "confirmed"],
            )

            booked_tables = existing_bookings.values_list("table_id", flat=True)
            available_tables = Table.objects.exclude(id__in=booked_tables)

            return JsonResponse(
                {
                    "available_tables": list(
                        available_tables.values("id", "number", "seats")
                    )
                }
            )
        except ValueError:
            return JsonResponse({"error": "Неверный формат даты или времени"})

    return JsonResponse({"error": "Не указаны дата или время"})
