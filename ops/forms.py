from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from .models import ShipRoleTemplate, RoleSlot
from .utils import get_ordered_user_queryset

class ShipRoleTemplateForm(forms.ModelForm):
    class Meta:
        model = ShipRoleTemplate
        fields = ("role_name", "slots")

class RoleSlotForm(forms.ModelForm):
    user = forms.ModelChoiceField(label="Utilisateur", queryset=User.objects.order_by("username"), required=False)
    user = forms.ModelChoiceField(
        label="Utilisateur",
        queryset=get_user_model()._default_manager.none(),
        required=False,
    )

    class Meta:
        model = RoleSlot
        fields = ("user", "status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = get_ordered_user_queryset()