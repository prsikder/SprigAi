from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", views.admin_home, name="admin_home"),
    path("admin/users/", views.admin_users, name="admin_users"),
    path("admin/contacts/", views.admin_contact_messages, name="admin_contacts"),
    path("admin/contacts/<int:pk>/status/", views.admin_update_contact_status, name="admin_update_contact_status"),
]
