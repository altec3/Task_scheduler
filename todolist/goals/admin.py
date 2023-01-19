from django.contrib import admin

from goals.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created', 'updated',)
    search_fields = ('title', 'author__username',)
