from django.urls import path

from . import views

app_name = "menu"

urlpatterns = [
    path("", views.MenuListView.as_view(), name="menu_list"),
    path(
        "category/<int:pk>/",
        views.MenuCategoryDetailView.as_view(),
        name="category_detail",
    ),
    path("item/<int:pk>/", views.MenuItemDetailView.as_view(), name="item_detail"),
    path("search/", views.menu_search, name="menu_search"),
]
