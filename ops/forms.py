from django import forms
from django.contrib.auth import get_user_model

from .models import Operation, ShipRoleTemplate, RoleSlot
from .utils import get_ordered_user_queryset


class ShipRoleTemplateForm(forms.ModelForm):
    class Meta:
        model = ShipRoleTemplate
        fields = ("role_name", "slots")
        widgets = {
            "role_name": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/10 bg-white/5 text-white px-3 py-2",
                    "placeholder": "Rôle",
                }
            ),
            "slots": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/10 bg-white/5 text-white px-3 py-2",
                    "min": 1,
                }
            ),
        }


class RoleSlotForm(forms.ModelForm):
    user = forms.ModelChoiceField(
@@ -35,25 +35,60 @@ class RoleSlotForm(forms.ModelForm):
    class Meta:
        model = RoleSlot
        fields = ("user", "status")
        widgets = {
            "user": forms.Select(
                attrs={
                    "class": "w-full rounded-xl border border-white/15 bg-black/40 px-3 py-2",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full rounded-xl border border-white/15 bg-black/40 px-3 py-2",
                }
            ),
        }

    def __init__(self, *args, user_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = user_queryset or get_ordered_user_queryset()
        self.fields["user"].queryset = qs
        self.fields["user"].empty_label = "— Libre —"

    @staticmethod
    def default_user_queryset():
        return get_ordered_user_queryset()


class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = ("title", "description", "highlighted_ship", "is_active")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/10 bg-white/5 text-white px-3 py-2",
                    "placeholder": "Nom de l’opération",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/10 bg-white/5 text-white px-3 py-3",
                    "rows": 4,
                    "placeholder": "Briefing, objectifs, instructions…",
                }
            ),
            "highlighted_ship": forms.Select(
                attrs={
                    "class": "w-full rounded-xl border border-white/10 bg-white/5 text-white px-3 py-2",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-white/20 bg-black/40 text-indigo-500 focus:ring-indigo-400",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["highlighted_ship"].empty_label = "— Aucun —"