import json

from django import forms
from django.contrib.auth import get_user_model

from .models import (
    Operation,
    OperationHighlightedShip,
    ShipRoleTemplate,
    RoleSlot,
    Ship,
)
from .utils import get_ordered_user_queryset


ROLE_PLACEHOLDERS = {
    "gunner": "Nom du gunner",
    "infantry": "Nom de l’escouade",
    "pilot": "Nom du pilote",
    "torpedo": "Nom de l’opérateur torpille",
}


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
        label="Utilisateur",
        queryset=get_user_model().objects.none(),
        required=False,
@@ -40,55 +56,158 @@ class RoleSlotForm(forms.ModelForm):
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
        fields = ("title", "description", "is_active")
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
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-white/20 bg-black/40 text-indigo-500 focus:ring-indigo-400",
                }
            ),
        }


class HighlightedShipForm(forms.Form):
    """Form used inside the dynamic highlighted ships formset."""

    ship = forms.ModelChoiceField(
        label="Vaisseau",
        queryset=Ship.objects.order_by("name"),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-xl border border-white/10 bg-white text-black px-3 py-2",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial") or {}
        super().__init__(*args, **kwargs)

        self.role_metadata: list[dict[str, object]] = []
        for role, label in OperationHighlightedShip.ROLE_CHOICES:
            field_name = self._role_field_name(role)
            field = forms.CharField(required=False, widget=forms.HiddenInput())
            self.fields[field_name] = field

            raw_value = self._initial_role_value(field_name, role, initial)
            entries = self._coerce_role_entries(raw_value)
            serialized = json.dumps(entries, ensure_ascii=False)

            field.initial = serialized
            field.widget.attrs.update(
                {
                    "data-role-store": role,
                    "data-initial": serialized,
                }
            )

            self.role_metadata.append(
                {
                    "role": role,
                    "label": label,
                    "placeholder": ROLE_PLACEHOLDERS.get(role, ""),
                    "initial": entries,
                    "field": self[field_name],
                }
            )

        delete_field = self.fields.get("DELETE")
        if delete_field is not None:
            delete_field.label = "Supprimer cette entrée"
            delete_field.widget = forms.CheckboxInput(
                attrs={
                    "class": "hidden",
                    "data-delete-field": "true",
                }
            )

    def _initial_role_value(self, field_name: str, role: str, initial: dict):
        if self.is_bound:
            return self.data.get(self.add_prefix(field_name), "")
        if field_name in initial:
            return initial[field_name]
        return initial.get(f"{role}_names", [])

    @staticmethod
    def _role_field_name(role: str) -> str:
        return f"{role}_entries"

    def _coerce_role_entries(self, value):
        if isinstance(value, (list, tuple)):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return []
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parts = [part.strip() for part in text.replace("\r", "").split("\n")]
                return [part for part in parts if part]
            else:
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
        return []

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("DELETE"):
            return cleaned_data

        ship = cleaned_data.get("ship")
        total_assigned = 0
        for role, _label in OperationHighlightedShip.ROLE_CHOICES:
            field_name = self._role_field_name(role)
            raw_value = cleaned_data.get(field_name, "")
            names = self._coerce_role_entries(raw_value)
            cleaned_data[field_name] = names
            total_assigned += len(names)

        if ship is None and total_assigned:
            raise forms.ValidationError(
                "Sélectionnez un vaisseau pour enregistrer les membres d’équipage."
            )
        return cleaned_data


HighlightedShipFormSet = forms.formset_factory(
    HighlightedShipForm,
    extra=1,
    can_delete=True,
)