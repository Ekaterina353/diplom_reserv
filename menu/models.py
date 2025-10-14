from django.db import models


class MenuCategory(models.Model):
    """Категория блюд в меню"""

    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка Bootstrap")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Категория меню"
        verbose_name_plural = "Категории меню"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Пункт меню (блюдо)"""

    name = models.CharField(max_length=200, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Описание блюда")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Категория",
    )
    image = models.ImageField(
        upload_to="menu_items/", blank=True, null=True, verbose_name="Фото блюда"
    )
    weight = models.CharField(max_length=50, blank=True, verbose_name="Вес/порция")
    is_vegetarian = models.BooleanField(default=False, verbose_name="Вегетарианское")
    is_spicy = models.BooleanField(default=False, verbose_name="Острое")
    is_available = models.BooleanField(default=True, verbose_name="Доступно")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок в категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"
        ordering = ["category__order", "order", "name"]

    def __str__(self):
        return f"{self.name} - {self.category.name}"

    @property
    def display_price(self):
        """Форматированная цена для отображения"""
        return f"{self.price} ₽"
