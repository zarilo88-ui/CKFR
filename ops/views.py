from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Ship, RoleSlot
from .forms import RoleSlotForm, ShipRoleTemplateForm

def is_planner(user):
    return user.is_superuser or user.groups.filter(name__in=["Planner", "Administrateur", "Planificateur"]).exists()

@login_required
def ships_list(request):
    cat = request.GET.get("cat")
    qs = Ship.objects.all()
    if cat:
        qs = qs.filter(category=cat)
    ships = qs.order_by("name")
    categories = [
        ("LF", "Chasseur léger"),
        ("MF", "Chasseur moyen"),
        ("HF", "Chasseur lourd"),
        ("MR", "Multirôle"),
        ("CAP", "Capital"),
    ]
    return render(request, "ops/ships_list.html", {"ships": ships, "categories": categories, "current_cat": cat})

@login_required
def ship_detail(request, pk):
    ship = get_object_or_404(Ship, pk=pk)
    slots_by_role = {}
    for slot in ship.role_slots.select_related("user").order_by("role_name", "index"):
        slots_by_role.setdefault(slot.role_name, []).append(slot)

    role_form = ShipRoleTemplateForm()
    can_edit = is_planner(request.user)

    if request.method == "POST" and can_edit and "role_name" in request.POST:
        role_form = ShipRoleTemplateForm(request.POST)
        if role_form.is_valid():
            rt = role_form.save(commit=False)
            rt.ship = ship
            rt.save()
            messages.success(request, "Rôle ajouté au vaisseau.")
            return redirect("ship_detail", pk=ship.pk)

    return render(request, "ops/ship_detail.html",
                  {"ship": ship, "slots_by_role": slots_by_role, "role_form": role_form, "can_edit": can_edit})

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
