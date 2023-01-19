from django.urls import path, include
from rest_framework import routers

from goals.views import CategoryViewSet

categories_router = routers.SimpleRouter()
categories_router.register('goal_category', CategoryViewSet)

urlpatterns = [
    path('', include(categories_router.urls)),
]
