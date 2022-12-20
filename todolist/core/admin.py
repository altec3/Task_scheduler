from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from core.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("username",)}),
        (None, {"fields": ("first_name", "last_name", "email")}),
        (
            None,
            {
                "fields": (
                    "is_active",
                    "is_staff",
                ),
            },
        ),
        (None, {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    # list page fields
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ("username", "first_name", "last_name", "email")
    # user page fields
    readonly_fields = ('last_login', 'date_joined')
    exclude = ['password']

    ordering = ("username",)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        is_superuser = request.user.is_superuser
        disabled_fields = set()
        defaults = {}

        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)

        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser',
            }
        for field in disabled_fields:
            if field in self.form.base_fields:
                self.form.base_fields[field].disabled = True

        return super().get_form(request, obj, **defaults)
