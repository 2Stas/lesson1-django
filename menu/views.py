from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal, InvalidOperation
from .models import Dish, Category, Drink


def home(request):
    return render(request, "menu/home.html")


def menu_list(request):
    dishes = Dish.objects.select_related("category").all()
    drinks = Drink.objects.filter(is_available=True)

    return render(
        request,
        "menu/menu_list.html",
        {"dishes": dishes, "drinks": drinks}
    )


def dish_detail(request, dish_id):
    dish = get_object_or_404(
        Dish.objects.select_related("category"),
        id=dish_id
    )

    return render(
        request,
        "menu/dish_detail.html",
        {"dish": dish}
    )


def dish_create(request):
    return dish_form(request)


def dish_update(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    return dish_form(request, dish)


def dish_form(request, dish=None):
    categories = Category.objects.all()
    error = None

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        price_text = request.POST.get("price", "").strip()
        category_id = request.POST.get("category", "")
        is_available = request.POST.get("is_available") == "on"

        values = {
            "name": name,
            "description": description,
            "price": price_text,
            "category_id": category_id,
            "is_available": is_available,
        }

        category = None
        price = None

        if not name:
            error = "Введи назву страви."
        elif len(name) > 150:
            error = "Назва не може перевищувати 150 символів."

        if error is None:
            try:
                price = Decimal(price_text)

                if not price.is_finite() or price <= 0:
                    error = "Ціна повинна бути більшою за нуль."
                elif price > Decimal("99999.99"):
                    error = "Максимальна ціна — 99999.99 грн."
                elif price.as_tuple().exponent < -2:
                    error = "Ціна може мати не більше двох знаків після коми."

            except InvalidOperation:
                error = "Введи коректну ціну, наприклад 125.50."

        if error is None:
            try:
                category = Category.objects.get(id=category_id)
            except (Category.DoesNotExist, ValueError, TypeError):
                error = "Обери наявну категорію."

        if error is None:
            if dish is None:
                dish = Dish()

            dish.name = name
            dish.description = description
            dish.price = price
            dish.category = category
            dish.is_available = is_available
            dish.save()

            if request.resolver_match.url_name == "dish_create":
                messages.success(request, "Dish successfully was added!")
            else:
                messages.success(request, "Dish successfully was updated!")

            return redirect(
                "menu:dish_detail",
                dish_id=dish.id
            )

    else:
        if dish is not None:
            values = {
                "name": dish.name,
                "description": dish.description,
                "price": str(dish.price),
                "category_id": str(dish.category_id),
                "is_available": dish.is_available,
            }
        else:
            values = {
                "name": "",
                "description": "",
                "price": "",
                "category_id": "",
                "is_available": True,
            }

    if not categories.exists():
        error = "Спочатку створи хоча б одну категорію."

    title = "Додати страву" if dish is None else "Редагувати страву"

    return render(
        request,
        "menu/dish_form.html",
        {
            "title": title,
            "dish": dish,
            "categories": categories,
            "values": values,
            "error": error,
        }
    )


def dish_delete(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    if request.method == "POST":
        dish.delete()
        messages.success(request, "dish was deleted successfully!")
        return redirect("menu:menu_list")
    
    return render(
        request,
        "menu/dish_confirm_delete.html",
        {"dish": dish}
    )
