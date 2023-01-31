from django.contrib import admin

from goals.models import Category, Goal, Comment, Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'updated',)
    search_fields = ('title',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'user', 'created', 'updated',)
    search_fields = ('title', 'user__username',)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'description', 'status', 'priority', 'due_date',)
    search_fields = ('title', 'user__username', 'status',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'goal', 'created',)
    search_fields = ('text', 'user__username',)
