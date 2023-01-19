from django.urls import path

from core import views

urlpatterns = [
    path('signup', views.UserCreateView.as_view(), name='user_create'),
    path('login', views.UserLoginView.as_view(), name='user_login'),
    path('profile', views.UserRetrieveView.as_view(), name='user_retrieve'),
    path('update_password', views.UpdatePasswordView.as_view(), name='password_update'),
]
