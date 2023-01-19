from rest_framework import serializers

from core.serializers import ProfileSerializer
from goals.models import Category


class CategoryCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default='author')

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'author',)


class CategoryListSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'author',)
