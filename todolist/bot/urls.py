from django.urls import path

from bot import views

urlpatterns = [
    path('verify', views.TgUserUpdateView.as_view(), name='update-tguser'),
]
