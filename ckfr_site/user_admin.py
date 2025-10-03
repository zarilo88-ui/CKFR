from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms

class MaskedPasswordWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return "********"  # always mask, no hash shown

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {
            "password": MaskedPasswordWidget(),  # mask password hash
        }

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    # keep same config as default, only password field is masked
    fieldsets = BaseUserAdmin.fieldsets
    add_fieldsets = BaseUserAdmin.add_fieldsets
