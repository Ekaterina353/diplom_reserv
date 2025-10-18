import datetime
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Booking, SiteContent, Table, TeamMember


class TableModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Table.objects.create(number=1, seats=4, description="Столик у окна", is_available=True)

    def test_table_creation(self):
        table = Table.objects.get(number=1)
        self.assertEqual(table.seats, 4)
        self.assertEqual(table.description, "Столик у окна")
        self.assertTrue(table.is_available)

    def test_table_str_representation(self):
        table = Table.objects.get(number=1)
        self.assertEqual(str(table), "Столик №1 (4 мест)")

    def test_table_meta_verbose_name(self):
        self.assertEqual(str(Table._meta.verbose_name), "Столик")

    def test_table_meta_verbose_name_plural(self):
        self.assertEqual(str(Table._meta.verbose_name_plural), "Столики")

    def test_table_meta_ordering(self):
        self.assertEqual(Table._meta.ordering, ["number"])


class BookingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = get_user_model().objects.create_user(username="testuser", password="testpassword")
        cls.table = Table.objects.create(number=1, seats=4)
        cls.booking = Booking.objects.create(
            user=cls.user,
            table=cls.table,
            date=datetime.date(2025, 10, 20),
            time=datetime.time(19, 00),
            guests_count=2,
            status="confirmed",
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.table, self.table)
        self.assertEqual(self.booking.date, datetime.date(2025, 10, 20))
        self.assertEqual(self.booking.time, datetime.time(19, 00))
        self.assertEqual(self.booking.guests_count, 2)
        self.assertEqual(self.booking.status, "confirmed")

    def test_booking_str_representation(self):
        expected_str = "Бронь Гость на 2025-10-20 19:00:00 (столик Столик №1 (4 мест))"
        self.assertEqual(str(self.booking), expected_str)

    def test_booking_meta_verbose_name(self):
        self.assertEqual(str(Booking._meta.verbose_name), "Бронирование")

    def test_booking_meta_verbose_name_plural(self):
        self.assertEqual(str(Booking._meta.verbose_name_plural), "Бронирования")

    def test_booking_meta_ordering(self):
        self.assertEqual(Booking._meta.ordering, ["-created_at"])

    def test_total_amount_property(self):
        self.booking.preorder_total = 50.00
        self.booking.deposit_amount = 20.00
        self.assertEqual(self.booking.total_amount, 70.00)

    def test_remaining_amount_property(self):
        self.booking.preorder_total = 50.00
        self.booking.deposit_amount = 20.00
        self.booking.deposit_paid = True
        self.assertEqual(self.booking.remaining_amount, 50.00)

        self.booking.deposit_paid = False
        self.assertEqual(self.booking.remaining_amount, 70.00)

    def test_requires_deposit_property(self):
        self.booking.has_preorder = True
        self.assertTrue(self.booking.requires_deposit)

        self.booking.has_preorder = False
        self.assertFalse(self.booking.requires_deposit)

    def test_can_be_cancelled_property(self):
        self.booking.has_preorder = False
        self.booking.status = "confirmed"
        self.assertTrue(self.booking.can_be_cancelled)

        self.booking.status = "pending"
        self.assertTrue(self.booking.can_be_cancelled)

        self.booking.status = "completed"
        self.assertFalse(self.booking.can_be_cancelled)

        self.booking.status = "cancelled"
        self.assertFalse(self.booking.can_be_cancelled)
        self.booking.status = "paid"
        self.assertFalse(self.booking.can_be_cancelled)

        self.booking.has_preorder = True
        self.booking.status = "confirmed"
        self.assertFalse(self.booking.can_be_cancelled)

    def test_booking_with_null_user(self):  # Учет null=True, blank=True в user
        null_booking = Booking.objects.create(
            user=None,
            table=self.table,
            date=datetime.date(2025, 10, 21),
            time=datetime.time(20, 00),
            guests_count=3,
        )
        self.assertIsNone(null_booking.user)  # Проверка, что user действительно None


class TeamMemberModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        TeamMember.objects.create(
            name="John Doe", role="Chef", bio="Experienced Chef", photo="team/johndoe.jpg"
        )

    def test_team_member_creation(self):
        team_member = TeamMember.objects.get(name="John Doe")
        self.assertEqual(team_member.role, "Chef")
        self.assertEqual(team_member.bio, "Experienced Chef")
        self.assertEqual(team_member.photo, "team/johndoe.jpg")

    def test_team_member_str_representation(self):
        team_member = TeamMember.objects.get(name="John Doe")
        self.assertEqual(str(team_member), "John Doe — Chef")

    def test_team_member_meta_verbose_name(self):
        self.assertEqual(str(TeamMember._meta.verbose_name), "Член команды")

    def test_team_member_meta_verbose_name_plural(self):
        self.assertEqual(str(TeamMember._meta.verbose_name_plural), "Члены команды")

    def test_team_member_meta_ordering(self):
        self.assertEqual(TeamMember._meta.ordering, ["name"])

    def test_team_member_blank_photo(self):
        member = TeamMember.objects.create(name="Jane Smith", role="Waiter", bio="Friendly waiter")
        self.assertIsNone(member.photo.name)  # Проверяем, что blank=True работает. photo.name будет None, а не ""


class SiteContentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteContent.objects.create(key="welcome_message", value="Welcome to our restaurant!")

    def test_site_content_creation(self):
        site_content = SiteContent.objects.get(key="welcome_message")
        self.assertEqual(site_content.value, "Welcome to our restaurant!")

    def test_site_content_str_representation(self):
        site_content = SiteContent.objects.get(key="welcome_message")
        self.assertEqual(str(site_content), "welcome_message")

    def test_site_content_meta_verbose_name(self):
        self.assertEqual(str(SiteContent._meta.verbose_name), "Контент сайта")

    def test_site_content_meta_verbose_name_plural(self):
        self.assertEqual(str(SiteContent._meta.verbose_name_plural), "Контент сайта")

    def test_site_content_meta_ordering(self):
        self.assertEqual(SiteContent._meta.ordering, ["key"])

    def test_site_content_unique_key(self):
        with self.assertRaises(Exception):  # Catching any exception as constraint errors vary by DB
            SiteContent.objects.create(key="welcome_message", value="Duplicate key")


# Дополнительные тесты для edge cases и разных вариантов STATUS_CHOICES
class BookingStatusTest(TestCase):  # Создаем новый класс для этих тестов, чтобы использовать setup
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = get_user_model().objects.create_user(username="testuser", password="testpassword")
        cls.table = Table.objects.create(number=1, seats=4)
        cls.booking = Booking.objects.create(
            user=cls.user,
            table=cls.table,
            date=datetime.date(2025, 10, 20),
            time=datetime.time(19, 00),
            guests_count=2,
            status="confirmed",
        )

    def test_booking_status_choices(self):
        for choice in Booking.STATUS_CHOICES:
            Booking.objects.create(
                user=self.user,
                table=self.table,
                date=datetime.date(2025, 10, 22),
                time=datetime.time(18, 00),
                guests_count=2,
                status=choice[0],
            )
            # Проверка, что создаются объекты с разными статусами, без ошибок
            self.assertTrue(Booking.objects.filter(status=choice[0]).exists())

    def test_booking_preorder_items_jsonfield(self):  # Проверяем JSONField
        preorder_data = [{"item": "Pizza", "quantity": 2}, {"item": "Salad", "quantity": 1}]
        booking = Booking.objects.create(
            user=self.user,
            table=self.table,
            date=datetime.date(2025, 10, 23),
            time=datetime.time(21, 00),
            guests_count=4,
            has_preorder=True,
            preorder_items=preorder_data,
        )
        retrieved_data = booking.preorder_items
        self.assertEqual(retrieved_data, preorder_data)  # Проверяем, что данные сохраняются и извлекаются верно

    def test_booking_deposit_fields(self):
        booking = Booking.objects.create(
            user=self.user,
            table=self.table,
            date=datetime.date(2025, 10, 24),
            time=datetime.time(12, 00),
            guests_count=2,
            deposit_amount=50.0,
        )
        self.assertFalse(booking.deposit_paid)
        self.assertIsNone(booking.deposit_paid_at)
        self.assertIsNone(booking.deposit_confirmed_by)
        self.assertIsNone(booking.deposit_confirmed_at)
        # (На этом этапе нужно было бы добавить в тест кейс тестового администратора для более полного покрытия
        # проверки по deposit_confirmed_by)

    def test_table_is_available_default(self):  # проверка значения по умолчанию
        table = Table.objects.create(number=2, seats=2)
        self.assertTrue(table.is_available)  # Проверка значения по умолчанию
