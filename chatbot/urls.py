from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chat_view, name="chat"),
    path("send/", views.send_message_view, name="send_message"),
    path("clear/", views.clear_chat_view, name="clear_chat"),
]
