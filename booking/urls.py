from django.urls import path

from . import views

app_name = "booking"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("booking/", views.booking_page, name="booking"),
    path("booking/success/", views.booking_success, name="booking_success"),
    path("booking/<int:booking_id>/", views.booking_detail, name="booking_detail"),
    path(
        "booking/<int:booking_id>/confirm-payment/",
        views.confirm_payment,
        name="confirm_payment",
    ),
    path(
        "booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"
    ),
    path("contact/", views.contact, name="contact"),
    path(
        "check-availability/", views.check_table_availability, name="check_availability"
    ),
]
