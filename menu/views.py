from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import MenuCategory, MenuItem


class MenuListView(ListView):
    """Представление для отображения полного меню с категориями"""

    model = MenuCategory
    template_name = "menu/menu_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        category_filter = self.request.GET.get("category")
        if category_filter:
            return (
                MenuCategory.objects.filter(is_active=True, id=category_filter)
                .prefetch_related("items")
                .order_by("order", "name")
            )
        else:
            return (
                MenuCategory.objects.filter(is_active=True)
                .prefetch_related("items")
                .order_by("order", "name")
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = None
        if self.request.GET.get("category"):
            try:
                context["category"] = MenuCategory.objects.get(
                    id=self.request.GET.get("category"), is_active=True
                )
            except MenuCategory.DoesNotExist:
                pass
        context["page_title"] = "Меню ресторана Dzūkija"
        context["page_description"] = "Традиционные литовские блюда и европейская кухня"
        return context


class MenuCategoryDetailView(DetailView):
    """Представление для отображения отдельной категории меню"""

    model = MenuCategory
    template_name = "menu/category_detail.html"
    context_object_name = "category"

    def get_queryset(self):
        return MenuCategory.objects.filter(is_active=True).prefetch_related("items")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Меню - {self.object.name}"
        context["page_description"] = self.object.description
        return context


class MenuItemDetailView(DetailView):
    """Представление для отображения отдельного блюда"""

    model = MenuItem
    template_name = "menu/item_detail.html"
    context_object_name = "item"

    def get_queryset(self):
        return MenuItem.objects.filter(is_available=True).select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.object.name
        context["page_description"] = (
            self.object.description[:100] + "..."
            if len(self.object.description) > 100
            else self.object.description
        )
        return context


def menu_search(request):
    """Поиск по меню"""
    query = request.GET.get("q", "")
    category_filter = request.GET.get("category", "")
    vegetarian_filter = request.GET.get("vegetarian", "")
    spicy_filter = request.GET.get("spicy", "")

    items = MenuItem.objects.filter(is_available=True).select_related("category")
    categories = MenuCategory.objects.filter(is_active=True)

    if query:
        items = items.filter(name__icontains=query) | items.filter(
            description__icontains=query
        )

    if category_filter:
        items = items.filter(category_id=category_filter)

    if vegetarian_filter == "true":
        items = items.filter(is_vegetarian=True)

    if spicy_filter == "true":
        items = items.filter(is_spicy=True)

    context = {
        "items": items,
        "categories": categories,
        "query": query,
        "selected_category": category_filter,
        "vegetarian_filter": vegetarian_filter,
        "spicy_filter": spicy_filter,
        "page_title": "Поиск по меню",
        "page_description": "Найдите любимые блюда в меню ресторана Dzūkija",
    }

    return render(request, "menu/menu_search.html", context)
