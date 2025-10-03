from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms

class MaskedPasswordWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return "********"

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {"password": MaskedPasswordWidget()}

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    fieldsets = BaseUserAdmin.fieldsets
    add_fieldsets = BaseUserAdmin.add_fieldsets
