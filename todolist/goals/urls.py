from django.urls import path, include

from goals.routers import CustomAPIRouter
from goals.views import BoardViewSet, CategoryViewSet, GoalViewSet, CommentViewSet

board_router = CustomAPIRouter(trailing_slash=False)
board_router.register('board', BoardViewSet)

category_router = CustomAPIRouter(trailing_slash=False)
category_router.register('goal_category', CategoryViewSet)

goal_router = CustomAPIRouter(trailing_slash=False)
goal_router.register('goal', GoalViewSet)

comment_router = CustomAPIRouter(trailing_slash=False)
comment_router.register('goal_comment', CommentViewSet)

app_name = 'goals'
urlpatterns = [
    path('', include(board_router.urls)),
    path('', include(category_router.urls)),
    path('', include(goal_router.urls)),
    path('', include(comment_router.urls)),
]
