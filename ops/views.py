from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Ship, ShipRoleTemplate, RoleSlot
from .forms import RoleSlotForm, ShipForm, ShipRoleTemplateForm

def is_planner(user):
    # Adjust group names if you localized them; superuser bypasses
    return user.is_superuser or user.groups.filter(name__in=["Planner", "Administrateur", "Planificateur"]).exists()

@login_required
def ships_list(request):
    ships = Ship.objects.order_by("name")
    return render(request, "ops/ships_list.html", {"ships": ships})

@login_required
def ship_detail(request, pk):
    ship = get_object_or_404(Ship, pk=pk)
    # Group slots by role name for display
    slots_by_role = {}
    for slot in ship.role_slots.select_related("user").order_by("role_name", "index"):
        slots_by_role.setdefault(slot.role_name, []).append(slot)

    # Simple inline add-a-role-template form for planners/admins
    role_form = ShipRoleTemplateForm()
    can_edit = is_planner(request.user)

    if request.method == "POST" and can_edit and "role_name" in request.POST:
        role_form = ShipRoleTemplateForm(request.POST)
        if role_form.is_valid():
            rt = role_form.save(commit=False)
            rt.ship = ship
            rt.save()  # signals will create missing RoleSlot rows
            messages.success(request, "Rôle ajouté au vaisseau.")
            return redirect("ship_detail", pk=ship.pk)

    return render(
        request,
        "ops/ship_detail.html",
        {"ship": ship, "slots_by_role": slots_by_role, "role_form": role_form, "can_edit": can_edit},
    )

@login_required
@user_passes_test(is_planner)
def role_slot_update(request, pk):
    slot = get_object_or_404(RoleSlot, pk=pk)
    if request.method == "POST":
        form = RoleSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, "Affectation mise à jour.")
    return redirect("ship_detail", pk=slot.ship_id)
