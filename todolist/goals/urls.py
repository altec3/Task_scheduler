from django.urls import path

from goals.views import CategoryViewSet, GoalViewSet, CommentViewSet

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
comment_create = CommentViewSet.as_view({'post': 'create'})
comment_list = CommentViewSet.as_view({'get': 'list'})
comment_detail = CommentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path('goal_category/create', category_create, name='category-create'),
    path('goal_category/list', category_list, name='category-list'),
    path('goal_category/<int:pk>', category_detail, name='category-detail'),
    path('goal/create', goal_create, name='goal-create'),
    path('goal/list', goal_list, name='goal-list'),
    path('goal/<int:pk>', goal_detail, name='goal-detail'),
    path('goal_comment/create', comment_create, name='comment-create'),
    path('goal_comment/list', comment_list, name='comment-list'),
    path('goal_comment/<int:pk>', comment_detail, name='comment-detail'),
]
