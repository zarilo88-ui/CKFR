from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist

from .models import ShipRoleTemplate, RoleSlot

class ShipRoleTemplateForm(forms.ModelForm):
    class Meta:
        model = ShipRoleTemplate
        fields = ("role_name", "slots")

class RoleSlotForm(forms.ModelForm):
    user = forms.ModelChoiceField(label="Utilisateur", queryset=User.objects.order_by("username"), required=False)
    user = forms.ModelChoiceField(
        label="Utilisateur",
        queryset=get_user_model().objects.none(),
        required=False,
    )

    class Meta:
        model = RoleSlot
        fields = ("user", "status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_model = get_user_model()
        order_field = getattr(user_model, "USERNAME_FIELD", "username")
        try:
            user_model._meta.get_field(order_field)
        except FieldDoesNotExist:
            order_field = "pk"
        self.fields["user"].queryset = user_model.objects.order_by(order_field)