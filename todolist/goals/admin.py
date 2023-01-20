from django.contrib import admin

from goals.models import Category, Goal


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created', 'updated',)
    search_fields = ('title', 'author__username',)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'description', 'status', 'priority', 'due_date',)
    search_fields = ('title', 'author__username', 'status',)

