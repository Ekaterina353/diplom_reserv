# import pytest
# from django.test import TestCase
# from django.db import IntegrityError
# from menu.models import MenuCategory, MenuItem  # Замените 'menu' на фактическое имя вашего приложения
#
#
# class MenuCategoryModelTest(TestCase):
#     """Тесты для модели MenuCategory."""
#
#     def setUp(self):
#         """Подготовка данных для тестов."""
#         self.category = MenuCategory.objects.create(name="Супы", description="Разные супы", order=1)
#
#     def test_category_creation(self):
#         """Проверка создания категории."""
#         self.assertEqual(self.category.name, "Супы")
#         self.assertEqual(self.category.description, "Разные супы")
#         self.assertEqual(self.category.order, 1)
#         self.assertTrue(self.category.is_active)
#
#     def test_category_name_max_length(self):
#         """Проверка ограничения длины названия категории."""
#         with self.assertRaises(IntegrityError):
#             MenuCategory.objects.create(name="Слишком длинное название категории, чтобы пройти валидацию",
#                                         description="Описание")
#
#     def test_category_ordering(self):
#         """Проверка правильности сортировки категорий."""
#         category2 = MenuCategory.objects.create(name="Салаты", order=0)
#         categories = MenuCategory.objects.all()
#         self.assertEqual(categories[0], category2)  # Салаты (order=0) должны быть первыми
#         self.assertEqual(categories[1], self.category)  # Супы (order=1) должны быть вторыми
#
#     def test_category_str_representation(self):
#         """Проверка строкового представления категории."""
#         self.assertEqual(str(self.category), "Супы")
#
#
# class MenuItemModelTest(TestCase):
#     """Тесты для модели MenuItem."""
#
#     def setUp(self):
#         """Подготовка данных для тестов."""
#         self.category = MenuCategory.objects.create(name="Напитки")
#         self.item = MenuItem.objects.create(
#             name="Чай",
#             description="Черный чай",
#             price=50.00,
#             category=self.category,
#         )
#
#     def test_item_creation(self):
#         """Проверка создания пункта меню."""
#         self.assertEqual(self.item.name, "Чай")
#         self.assertEqual(self.item.price, 50.00)
#         self.assertEqual(self.item.category, self.category)
#
#     def test_item_display_price(self):
#         """Проверка форматирования цены."""
#         self.assertEqual(self.item.display_price, "50.00 ₽")
#
#     def test_item_str_representation(self):
#         """Проверка строкового представления пункта меню."""
#         self.assertEqual(str(self.item), "Чай - Напитки")
#
#     def test_item_ordering(self):
#         """Проверка сортировки пунктов меню."""
#         item2 = MenuItem.objects.create(
#             name="Кофе",
#             description="Черный кофе",
#             price=100.00,
#             category=self.category,
#             order=0  # Установим order для второго элемента
#         )
#         items = MenuItem.objects.all()
#         self.assertEqual(items[0], item2)  # Кофе должен быть первым, т.к. order=0
#         self.assertEqual(items[1], self.item)
#
#     def test_item_vegetarian(self):
#         """Проверка вегетарианского пункта меню."""
#         item = MenuItem.objects.create(
#             name="Салат Цезарь",
#             description="Салат...",
#             price=250.00,
#             category=self.category,
#             is_vegetarian=True
#         )
#         self.assertTrue(item.is_vegetarian)
