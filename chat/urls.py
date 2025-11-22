from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("session/<int:session_id>/", views.chat_view, name="chat"),
    path("api/session/<int:session_id>/send/", views.send_message_api, name="send_message"),
]
