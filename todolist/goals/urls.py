from django.urls import path

from goals.views import CategoryViewSet

category_create = CategoryViewSet.as_view({'post': 'create'})
category_list = CategoryViewSet.as_view({'get': 'list'})
category_detail = CategoryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path('goal_category/create', category_create, name='category_create'),
    path('goal_category/list', category_list, name='category_list'),
    path('goal_category/<int:pk>', category_detail, name='category_detail'),
]
