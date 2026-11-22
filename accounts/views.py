from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success( request, f"Account was successfully created! Hello, {user.username}!"
            )

            return redirect("menu:menu_list")
    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def logout_account(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Ви успішно вийшли з акаунту.")
        return redirect("menu:menu_list")

    return render(request, "accounts/logout.html")