from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import redirect, render

from booking.models import Booking

from .forms import CustomUserChangeForm, CustomUserCreationForm


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password"].widget.attrs.update({"class": "form-control"})
        self.fields["username"].label = "Имя пользователя"
        self.fields["password"].label = "Пароль"


def register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect("user:profile")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически входим в систему после регистрации
            login(request, user)
            messages.success(
                request, "Регистрация прошла успешно! Добро пожаловать в Žemaičiai!"
            )
            return redirect("user:profile")
    else:
        form = CustomUserCreationForm()

    return render(request, "user/register.html", {"form": form})


def user_login(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect("user:profile")

    form = StyledAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                messages.success(
                    request,
                    f'Добро пожаловать, {getattr(user, "first_name", "") or getattr(user, "username", "")}!',
                )
                return redirect("user:profile")
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")

    return render(request, "user/login.html", {"form": form})


@login_required
def profile(request):
    """Личный кабинет пользователя"""
    user = request.user
    bookings = Booking.objects.filter(user=user).order_by("-created_at")

    # Статистика
    total_bookings = bookings.count()
    active_bookings = bookings.filter(status__in=["paid", "confirmed"]).count()
    pending_bookings = bookings.filter(status="pending").count()
    completed_bookings = bookings.filter(status="completed").count()

    context = {
        "user": user,
        "bookings": bookings[:5],  # Последние 5 бронирований
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "pending_bookings": pending_bookings,
        "completed_bookings": completed_bookings,
    }
    return render(request, "user/profile.html", context)


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("user:profile")
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, "user/edit_profile.html", {"form": form})


@login_required
def my_bookings(request):
    """История бронирований пользователя"""
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")
    context = {
        "bookings": bookings,
    }
    return render(request, "user/my_bookings.html", context)


def logout_view(request):
    """Выход пользователя с перенаправлением на главную"""
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect("booking:home")
