from django.urls import path

from core import views

urlpatterns = [
    path('signup', views.UserCreateView.as_view(), name='user_create'),
    path('login', views.UserLoginView.as_view(), name='user_login'),
]
