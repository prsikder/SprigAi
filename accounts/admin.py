from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class SprigUserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "role", "district", "is_staff", "created_at"]
    list_filter = ["role", "district", "is_staff", "is_active"]
    fieldsets = UserAdmin.fieldsets + (
        ("SprigAI Profile", {"fields": ("role", "phone", "district", "profile_image")}),
    )
