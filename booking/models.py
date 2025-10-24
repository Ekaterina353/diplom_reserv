from django.contrib.auth import get_user_model
from django.db import models


class Table(models.Model):
    number = models.PositiveIntegerField(unique=True, verbose_name="Номер столика")
    seats = models.PositiveIntegerField(verbose_name="Количество мест")
    description = models.CharField(max_length=255, blank=True, verbose_name="Описание")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"
        ordering = ["number"]

    def __str__(self):
        return f"Столик №{self.number} ({self.seats} мест)"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает предоплаты"),
        ("paid", "Предоплата внесена"),
        ("confirmed", "Подтверждено"),
        ("completed", "Завершено"),
        ("cancelled", "Отменено"),
    ]

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    name = models.CharField(max_length=100, default="Гость", verbose_name="Имя")
    phone = models.CharField(max_length=20, default="", verbose_name="Телефон")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Столик")
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Время")
    guests_count = models.PositiveIntegerField(verbose_name="Количество гостей")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default="confirmed",
        verbose_name="Статус",
    )
    comments = models.TextField(blank=True, verbose_name="Комментарий")
    preorder_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Сумма предзаказа"
    )
    deposit_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Сумма предоплаты"
    )
    deposit_paid = models.BooleanField(default=False, verbose_name="Предоплата внесена")
    deposit_paid_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата внесения предоплаты"
    )
    deposit_confirmed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_deposits",
        verbose_name="Подтвердил администратор",
    )
    deposit_confirmed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата подтверждения администратором"
    )

    # Поля для предзаказа меню
    has_preorder = models.BooleanField(default=False, verbose_name="Есть предзаказ")
    preorder_items = models.JSONField(
        default=list, blank=True, verbose_name="Предзаказанные блюда"
    )

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Бронь {self.name} на {self.date} {self.time} (столик {self.table})"

    @property
    def total_amount(self):
        """Общая сумма к оплате"""
        return self.preorder_total + self.deposit_amount

    @property
    def remaining_amount(self):
        """Оставшаяся сумма к оплате"""
        if self.deposit_paid:
            return self.preorder_total
        return self.total_amount

    @property
    def requires_deposit(self):
        """Требуется ли предоплата"""
        return self.has_preorder

    @property
    def can_be_cancelled(self):
        """Можно ли отменить бронирование"""
        return not self.has_preorder and self.status in ["confirmed", "pending"]


class TeamMember(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    role = models.CharField(max_length=100, verbose_name="Должность")
    bio = models.TextField(verbose_name="О себе")
    photo = models.ImageField(
        upload_to="team/", blank=True, null=True, verbose_name="Фото"
    )

    class Meta:
        verbose_name = "Член команды"
        verbose_name_plural = "Члены команды"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} — {self.role}"


class SiteContent(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="Ключ")
    value = models.TextField(verbose_name="Значение")

    class Meta:
        verbose_name = "Контент сайта"
        verbose_name_plural = "Контент сайта"
        ordering = ["key"]

    def __str__(self):
        return self.key
