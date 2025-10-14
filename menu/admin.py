from django.contrib import admin
from django.utils.html import format_html

from .models import MenuCategory, MenuItem


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "is_active", "items_count", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    list_editable = ["order", "is_active"]
    ordering = ["order", "name"]

    fieldsets = (
        ("Основная информация", {"fields": ("name", "description")}),
        ("Настройки отображения", {"fields": ("order", "is_active")}),
    )

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = "Количество блюд"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "price_display",
        "weight",
        "order",
        "is_vegetarian",
        "is_spicy",
        "is_available",
        "image_preview",
    ]
    list_filter = [
        "category",
        "is_vegetarian",
        "is_spicy",
        "is_available",
        "created_at",
    ]
    search_fields = ["name", "description", "category__name"]
    list_editable = ["order", "is_available", "is_vegetarian", "is_spicy"]
    ordering = ["category__order", "order", "name"]

    fieldsets = (
        ("Основная информация", {"fields": ("name", "description", "category")}),
        ("Цена и порция", {"fields": ("price", "weight")}),
        ("Изображение", {"fields": ("image",)}),
        ("Характеристики", {"fields": ("is_vegetarian", "is_spicy", "is_available")}),
        ("Порядок отображения", {"fields": ("order",)}),
    )

    def price_display(self, obj):
        return obj.display_price

    price_display.short_description = "Цена"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url,
            )
        return "Нет фото"

    image_preview.short_description = "Фото"
