from django.urls import path

from goals.views import CategoryViewSet, GoalViewSet

category_create = CategoryViewSet.as_view({'post': 'create'})
category_list = CategoryViewSet.as_view({'get': 'list'})
category_detail = CategoryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
goal_create = GoalViewSet.as_view({'post': 'create'})
goal_list = GoalViewSet.as_view({'get': 'list'})
goal_detail = GoalViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path('goal_category/create', category_create, name='category_create'),
    path('goal_category/list', category_list, name='category_list'),
    path('goal_category/<int:pk>', category_detail, name='category_detail'),
    path('goal/create', goal_create, name='goal_create'),
    path('goal/list', goal_list, name='goal_list'),
    path('goal/<int:pk>', goal_detail, name='goal_detail'),
]
