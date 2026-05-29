from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from projects.utils import paginate_queryset

from .forms import (
    UserChangePasswordForm,
    UserEditProfileForm,
    UserLoginForm,
    UserRegistrationForm,
)
from .models import User

PARTICIPANT_FILTERS = {
    "owners-of-favorite-projects": lambda user: User.objects.filter(
        owned_projects__in=user.favorites.all()
    ),
    "owners-of-participating-projects": lambda user: User.objects.filter(
        owned_projects__in=user.participated_projects.all()
    ),
    "interested-in-my-projects": lambda user: User.objects.filter(
        favorites__owner=user
    ),
    "participants-of-my-projects": lambda user: User.objects.filter(
        participated_projects__owner=user
    ),
}


def participants_list(request):
    queryset = User.objects.all().order_by("id")
    active_filter = None

    if request.user.is_authenticated:
        active_filter = request.GET.get("filter")
        if active_filter in PARTICIPANT_FILTERS:
            queryset = PARTICIPANT_FILTERS[active_filter](request.user).distinct().order_by("id")

    page_obj, query_prefix = paginate_queryset(request, queryset)
    return render(
        request,
        "users/participants.html",
        {
            "participants": queryset,
            "page_obj": page_obj,
            "query_prefix": query_prefix,
            "active_filter": active_filter,
        },
    )


def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, "users/user-details.html", {"user": user})


def register(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("projects:list")
    else:
        form = UserLoginForm()
    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("projects:list")


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserEditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = UserEditProfileForm(instance=request.user)
    return render(
        request,
        "users/edit_profile.html",
        {"form": form, "user": request.user},
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = UserChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            login(request, request.user)
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = UserChangePasswordForm(request.user)
    return render(request, "users/change_password.html", {"form": form})
