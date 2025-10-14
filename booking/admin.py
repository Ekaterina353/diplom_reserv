from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Booking, SiteContent, Table, TeamMember


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ["number", "seats", "description", "is_available"]
    list_filter = ["is_available", "seats"]
    search_fields = ["number", "description"]
    ordering = ["number"]
    list_editable = ["is_available"]

    fieldsets = (
        ("Основная информация", {"fields": ("number", "seats", "description")}),
        ("Статус", {"fields": ("is_available",)}),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "phone",
        "table",
        "date",
        "time",
        "guests_count",
        "status",
        "preorder_info",
        "payment_info",
        "admin_actions",
    ]
    list_filter = [
        "status",
        "date",
        "table",
        "has_preorder",
        "deposit_paid",
        "created_at",
    ]
    search_fields = ["name", "phone", "comments"]
    ordering = ["-created_at"]
    date_hierarchy = "date"
    readonly_fields = [
        "created_at",
        "deposit_paid_at",
        "deposit_confirmed_by",
        "deposit_confirmed_at",
        "preorder_items_display",
    ]
    list_editable = ["status"]
    actions = ["confirm_payment_action"]

    fieldsets = (
        ("Информация о клиенте", {"fields": ("user", "name", "phone")}),
        ("Детали бронирования", {"fields": ("table", "date", "time", "guests_count")}),
        (
            "Предзаказ и оплата",
            {
                "fields": (
                    "has_preorder",
                    "preorder_total",
                    "preorder_items_display",
                    "deposit_amount",
                    "deposit_paid",
                    "deposit_paid_at",
                    "deposit_confirmed_by",
                    "deposit_confirmed_at",
                )
            },
        ),
        ("Статус и комментарии", {"fields": ("status", "comments")}),
        ("Системная информация", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def preorder_info(self, obj):
        if obj.has_preorder:
            return format_html(
                '<span style="color: #E6B325;">✓ {}</span>', f"{obj.preorder_total} ₽"
            )
        return "—"

    preorder_info.short_description = "Предзаказ"

    def payment_info(self, obj):
        if obj.has_preorder:
            if obj.deposit_paid:
                return format_html(
                    '<span style="color: #28a745;">✓ {}</span>',
                    f"{obj.deposit_amount} ₽",
                )
            elif obj.deposit_amount > 0:
                return format_html(
                    '<span style="color: #ffc107;">⏳ {}</span>',
                    f"{obj.deposit_amount} ₽",
                )
            else:
                return format_html('<span style="color: #dc3545;">❌ Требуется</span>')
        else:
            return format_html('<span style="color: #6c757d;">Не требуется</span>')

    payment_info.short_description = "Предоплата"

    def preorder_items_display(self, obj):
        if obj.has_preorder and obj.preorder_items:
            items_html = "<ul style='margin: 0; padding-left: 20px;'>"
            for item in obj.preorder_items:
                quantity = item.get("quantity", 1)
                if quantity > 1:
                    items_html += (
                        f"<li>{item['name']} x{quantity} = {item['total']} ₽</li>"
                    )
                else:
                    items_html += f"<li>{item['name']} - {item['price']} ₽</li>"
            items_html += "</ul>"
            return format_html(items_html)
        return "Нет предзаказа"

    preorder_items_display.short_description = "Предзаказанные блюда"

    def admin_actions(self, obj):
        """Действия администратора"""
        if obj.status == "pending" and obj.has_preorder:
            return format_html(
                '<a href="{}" class="button" style="background: #28a745; color: white; '
                'padding: 5px 10px; text-decoration: none; border-radius: 3px;">Подтвердить предоплату</a>',
                f"/admin/booking/booking/{obj.id}/confirm-payment/",
            )
        elif obj.deposit_paid and obj.deposit_confirmed_by:
            return format_html(
                '<span style="color: #28a745;">✓ Подтверждено {}</span>',
                obj.deposit_confirmed_by.get_full_name()
                or obj.deposit_confirmed_by.username,
            )
        return "—"

    admin_actions.short_description = "Действия"

    def confirm_payment_action(self, request, queryset):
        """Массовое подтверждение предоплат"""
        confirmed_count = 0
        for booking in queryset:
            if booking.status == "pending" and booking.has_preorder:
                booking.status = "paid"
                booking.deposit_paid = True
                booking.deposit_paid_at = timezone.now()
                booking.deposit_confirmed_by = request.user
                booking.deposit_confirmed_at = timezone.now()
                booking.save()
                confirmed_count += 1

        if confirmed_count > 0:
            self.message_user(request, f"Подтверждено {confirmed_count} предоплат.")
        else:
            self.message_user(request, "Нет бронирований для подтверждения предоплаты.")

    confirm_payment_action.short_description = (
        "Подтвердить предоплату для выбранных бронирований"
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "photo_preview"]
    search_fields = ["name", "role"]
    ordering = ["name"]

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.photo.url,
            )
        return "Нет фото"

    photo_preview.short_description = "Фото"


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ["key", "value_preview"]
    search_fields = ["key", "value"]
    ordering = ["key"]

    def value_preview(self, obj):
        if len(obj.value) > 100:
            return obj.value[:100] + "..."
        return obj.value

    value_preview.short_description = "Значение"


# Настройки админки
admin.site.site_header = "Администрирование Dzūkija"
admin.site.site_title = "Dzūkija Admin"
admin.site.index_title = "Панель управления рестораном"
