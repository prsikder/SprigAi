import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import (
    ProfileForm,
    SprigAdminLoginForm,
    SprigLoginForm,
    SprigPasswordChangeForm,
    SprigSignupForm,
)
from .models import User

logger = logging.getLogger("sprigai")


def _resolve_username(identifier):
    """Allow login with either username or email."""
    if "@" in identifier:
        try:
            return User.objects.get(email__iexact=identifier).username
        except User.DoesNotExist:
            return identifier
    return identifier


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    if request.method == "POST":
        form = SprigSignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, "Welcome to SprigAI! Your account has been created.")
                return redirect("dashboard:home")
            except Exception:
                logger.exception("Signup failed")
                messages.error(request, "We couldn't create your account. Please try again.")
    else:
        form = SprigSignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    if request.method == "POST":
        form = SprigLoginForm(request, data=request.POST)
        identifier = request.POST.get("username", "")
        password = request.POST.get("password", "")
        username = _resolve_username(identifier)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get("next") or "dashboard:home"
            return redirect(next_url)
        messages.error(request, "Invalid username/email or password.")
    else:
        form = SprigLoginForm()
    return render(request, "accounts/login.html", {"form": form})


def admin_login_view(request):
    """A visually distinct admin login flow, still backed by Django auth."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard:admin_home")
    if request.method == "POST":
        identifier = request.POST.get("username", "")
        password = request.POST.get("password", "")
        username = _resolve_username(identifier)
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, "Welcome to the SprigAI admin dashboard.")
            return redirect("dashboard:admin_home")
        messages.error(request, "Invalid admin credentials or insufficient permissions.")
    form = SprigAdminLoginForm()
    return render(request, "accounts/admin_login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. See you soon!")
    return redirect("core:landing")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def password_change_view(request):
    if request.method == "POST":
        form = SprigPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("accounts:profile")
    else:
        form = SprigPasswordChangeForm(user=request.user)
    return render(request, "accounts/password_change.html", {"form": form})
