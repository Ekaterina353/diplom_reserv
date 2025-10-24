import re
from datetime import date, time, timedelta
from decimal import Decimal

from django import forms

from .models import Booking, Table


class BookingForm(forms.ModelForm):
    """Форма бронирования столика"""

    # Добавляем поля для выбора блюд с количеством
    # Эти поля будут создаваться динамически в __init__
    selected_items = forms.CharField(
        required=False, widget=forms.HiddenInput(), label="Выбранные блюда"
    )

    # Поле для предоплаты (только при предзаказе)
    deposit_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        label="Сумма предоплаты (₽)",
        help_text="Требуется только при предзаказе блюд",
    )

    class Meta:
        model = Booking
        fields = ["name", "phone", "date", "time", "guests_count", "comments"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+7 (999) 123-45-67"}
            ),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "guests_count": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "max": "20"}
            ),
            "comments": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "name": "Ваше имя",
            "phone": "Телефон",
            "date": "Дата",
            "time": "Время",
            "guests_count": "Количество гостей",
            "comments": "Комментарий",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Устанавливаем минимальную дату на сегодня
        self.fields["date"].widget.attrs["min"] = date.today().isoformat()

        # Создаем выбор времени с интервалом в 10 минут
        time_choices = []
        for hour in range(10, 22):  # с 10:00 до 21:00
            for minute in [0, 10, 20, 30, 40, 50]:
                time_str = f"{hour:02d}:{minute:02d}"
                time_choices.append((time_str, time_str))

        # Добавляем 22:00
        time_choices.append(("22:00", "22:00"))

        self.fields["time"] = forms.ChoiceField(
            choices=time_choices,
            label="Время",
            widget=forms.Select(attrs={"class": "form-control"}),
        )

        # Обновляем выбор столиков с описаниями
        table_choices = []
        tables = Table.objects.filter(is_available=True).order_by("number")
        for table in tables:
            description = f" - {table.description}" if table.description else ""
            table_choices.append(
                (table.id, f"Столик №{table.number} ({table.seats} мест){description}")
            )

        self.fields["table"] = forms.ChoiceField(
            choices=table_choices,
            label="Столик",
            widget=forms.Select(attrs={"class": "form-control"}),
        )

        # Загружаем доступные блюда из меню и создаем поля количества
        try:
            from menu.models import MenuItem

            menu_items = MenuItem.objects.filter(is_available=True).select_related(
                "category"
            )

            # Создаем динамические поля для каждого блюда
            for item in menu_items:
                field_name = f"item_{item.id}_quantity"
                self.fields[field_name] = forms.IntegerField(
                    min_value=0,
                    max_value=20,  # Максимум 20 порций одного блюда
                    required=False,
                    initial=0,
                    widget=forms.NumberInput(
                        attrs={
                            "class": "form-control item-quantity",
                            "data-item-id": item.id,
                            "data-item-price": str(item.price),
                            "data-item-name": item.name,
                            "min": "0",
                            "max": "20",
                            "style": "width: 80px;",
                        }
                    ),
                    label=f"{item.name} ({item.price} ₽)",
                )

            # Сохраняем список блюд для использования в шаблоне
            self.menu_items = menu_items
        except ImportError:
            self.fields["selected_items"].choices = []

        # Если пользователь авторизован, предлагаем его имя как начальное значение
        if user and user.is_authenticated:
            full_name = f"{user.first_name} {user.last_name}".strip()
            if full_name:
                self.fields["name"].initial = full_name

    def clean_phone(self):
        """Проверка корректности телефона"""
        phone = self.cleaned_data["phone"]
        if not phone:
            raise forms.ValidationError("Пожалуйста, укажите номер телефона для связи.")

        # Удаляем все пробелы, дефисы, скобки и другие символы
        phone_clean = re.sub(r"[\s\-\(\)\+]", "", phone)

        # Проверяем, что остались только цифры
        if not phone_clean.isdigit():
            raise forms.ValidationError(
                "Номер телефона должен содержать только цифры. Пример: +7 (999) 123-45-67"
            )

        # Проверяем длину (должно быть 10-11 цифр для российских номеров)
        if len(phone_clean) < 10:
            raise forms.ValidationError(
                "Номер телефона должен содержать минимум 10 цифр. Пример: +7 (999) 123-45-67"
            )

        if len(phone_clean) > 11:
            raise forms.ValidationError(
                "Номер телефона слишком длинный. Проверьте правильность ввода."
            )

        # Если 11 цифр, первая должна быть 7 или 8
        if len(phone_clean) == 11:
            if phone_clean[0] not in ["7", "8"]:
                raise forms.ValidationError(
                    "Номер телефона должен начинаться с 7 или 8. Пример: +7 (999) 123-45-67"
                )

        # Форматируем номер для сохранения
        if len(phone_clean) == 11:
            return f"+7{phone_clean[1:]}"
        else:
            return f"+7{phone_clean}"

    def clean_name(self):
        """Проверка имени"""
        name = self.cleaned_data["name"]
        if not name or not name.strip():
            raise forms.ValidationError("Пожалуйста, укажите ваше имя.")

        if len(name.strip()) < 2:
            raise forms.ValidationError("Имя должно содержать минимум 2 символа.")

        if len(name.strip()) > 50:
            raise forms.ValidationError("Имя слишком длинное. Максимум 50 символов.")

        return name.strip()

    def clean_date(self):
        """Проверка даты"""
        booking_date = self.cleaned_data["date"]
        if not booking_date:
            raise forms.ValidationError("Пожалуйста, выберите дату бронирования.")

        if booking_date < date.today():
            raise forms.ValidationError(
                "Нельзя бронировать на прошедшую дату. Выберите сегодняшнюю или будущую дату."
            )

        # Проверяем, что дата не слишком далеко в будущем (например, не более года)
        max_date = date.today() + timedelta(days=365)
        if booking_date > max_date:
            raise forms.ValidationError("Нельзя бронировать более чем на год вперед.")

        return booking_date

    def clean_time(self):
        """Проверка времени"""
        time_str = self.cleaned_data["time"]
        if not time_str:
            raise forms.ValidationError("Пожалуйста, выберите время бронирования.")

        try:
            # Преобразуем строку времени в объект time для валидации
            hour, minute = map(int, time_str.split(":"))
            booking_time = time(hour, minute)

            if booking_time < time(10, 0) or booking_time > time(22, 0):
                raise forms.ValidationError(
                    "Ресторан работает с 10:00 до 22:00. Выберите время в этом диапазоне."
                )

            return time_str  # Возвращаем строку для сохранения в базе
        except ValueError:
            raise forms.ValidationError(
                "Неверный формат времени. Выберите время из списка."
            )

    def clean_guests_count(self):
        """Проверка количества гостей"""
        guests_count = self.cleaned_data["guests_count"]
        if not guests_count:
            raise forms.ValidationError("Пожалуйста, укажите количество гостей.")

        if guests_count < 1:
            raise forms.ValidationError("Количество гостей должно быть не менее 1.")

        if guests_count > 20:
            raise forms.ValidationError("Максимальное количество гостей - 20 человек.")

        return guests_count

    def clean_table(self):
        """Проверка выбора столика"""
        table = self.cleaned_data.get("table")
        if not table:
            raise forms.ValidationError("Пожалуйста, выберите столик для бронирования.")

        try:
            table_obj = Table.objects.get(id=int(table))
            if not table_obj.is_available:
                raise forms.ValidationError(
                    "Выбранный столик недоступен для бронирования."
                )
        except (Table.DoesNotExist, ValueError):
            raise forms.ValidationError("Выбранный столик не найден.")

        return table

    def clean_deposit_amount(self):
        """Проверка суммы предоплаты"""
        deposit = self.cleaned_data.get("deposit_amount", 0)

        # Проверяем, есть ли выбранные блюда с количеством > 0
        has_items = False
        for field_name, value in self.cleaned_data.items():
            if (
                    field_name.startswith("item_")
                    and field_name.endswith("_quantity")
                    and value
                    and value > 0
            ):
                has_items = True
                break

        # Предоплата требуется только при предзаказе
        if has_items and deposit < 500:
            raise forms.ValidationError(
                "При предзаказе минимальная сумма предоплаты составляет 500 ₽ или 30% от суммы заказа."
            )

        return deposit or 0

    def clean(self):
        """Проверка всей формы"""
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time_str = cleaned_data.get("time")
        table = cleaned_data.get("table")
        guests_count = cleaned_data.get("guests_count")

        deposit_amount = cleaned_data.get("deposit_amount", 0)

        # Проверяем, что количество гостей не превышает вместимость столика
        if table and guests_count:
            try:
                table_obj = Table.objects.get(id=int(table))
                if guests_count > table_obj.seats:
                    raise forms.ValidationError(
                        f"Столик №{table_obj.number} вмещает максимум {table_obj.seats} человек. "
                        f"Выберите другой столик или уменьшите количество гостей."
                    )
            except (Table.DoesNotExist, ValueError):
                pass

        if date and time_str and table:
            try:
                # Преобразуем строку времени в объект time для сравнения
                hour, minute = map(int, time_str.split(":"))

                # Проверяем, не занят ли столик
                existing_booking = Booking.objects.filter(
                    table_id=int(table),
                    date=date,
                    time=time_str,
                    status__in=["pending", "paid", "confirmed"],
                ).exists()

                if existing_booking:
                    raise forms.ValidationError(
                        "Этот столик уже забронирован на указанное время. "
                        "Выберите другое время или другой столик."
                    )
            except ValueError:
                pass  # Ошибка времени уже обработана в clean_time

        # Рассчитываем сумму предзаказа на основе количества блюд
        preorder_total = Decimal("0")
        preorder_items = []

        try:
            from menu.models import MenuItem

            for field_name, quantity in self.cleaned_data.items():
                if (
                        field_name.startswith("item_")
                        and field_name.endswith("_quantity")
                        and quantity
                        and quantity > 0
                ):
                    # Извлекаем ID блюда из имени поля
                    item_id = field_name.replace("item_", "").replace("_quantity", "")
                    try:
                        item = MenuItem.objects.get(id=item_id, is_available=True)
                        item_total = item.price * quantity
                        preorder_total += item_total
                        preorder_items.append(
                            {
                                "id": item.id,
                                "name": item.name,
                                "price": float(item.price),
                                "quantity": quantity,
                                "total": float(item_total),
                                "category": item.category.name,
                            }
                        )
                    except MenuItem.DoesNotExist:
                        pass
        except ImportError:
            pass

        # Проверяем предоплату только при предзаказе
        if preorder_total > 0:
            min_deposit = max(
                Decimal("500"), preorder_total * Decimal("0.3")
            )  # 30% от суммы предзаказа
            if deposit_amount < min_deposit:
                raise forms.ValidationError(
                    f"При предзаказе на сумму {preorder_total} ₽ "
                    f"минимальная предоплата составляет {min_deposit} ₽."
                )

        # Сохраняем рассчитанные данные
        cleaned_data["preorder_total"] = preorder_total
        cleaned_data["preorder_items"] = preorder_items
        cleaned_data["has_preorder"] = len(preorder_items) > 0

        return cleaned_data


class ContactForm(forms.Form):
    """Форма обратной связи"""

    name = forms.CharField(
        max_length=100,
        label="Ваше имя",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    subject = forms.CharField(
        max_length=200,
        label="Тема",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    message = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}),
    )
