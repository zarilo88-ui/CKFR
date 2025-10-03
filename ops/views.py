"""Views for the operations module."""

from collections import defaultdict, OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import RoleSlotForm, ShipRoleTemplateForm
from .models import RoleSlot, Ship

STATUS_BADGES = {
    "open": "bg-white/10 text-white/60 border border-white/20",
    "assigned": "bg-amber-500/20 text-amber-200 border border-amber-500/40",
    "confirmed": "bg-emerald-500/20 text-emerald-200 border border-emerald-500/40",
}


def is_planner(user):
    """Return True if the user can manage ship allocations."""

    return user.is_superuser or user.groups.filter(
        name__in=["Planner", "Administrateur", "Planificateur"]
    ).exists()


@login_required
def ships_list(request):
    """Display the list of ships, optionally filtered by category."""

    category = request.GET.get("cat")
    queryset = Ship.objects.all()
    if category:
        queryset = queryset.filter(category=category)
    ships = queryset.order_by("name")

    return render(
        request,
        "ops/ships_list.html",
        {
            "ships": ships,
            "categories": Ship.CATEGORY_CHOICES,
            "current_cat": category,
        },
    )


@login_required
def ships_allocation(request):
    """Show all ships with their crew allocations."""

    ships = list(
        Ship.objects.prefetch_related(
            Prefetch(
                "role_slots",
                queryset=RoleSlot.objects.select_related("user").order_by(
                    "role_name", "index"
                ),
            )
        ).order_by("category", "name")
    )

    can_edit = is_planner(request.user)
    user_queryset = RoleSlotForm.default_user_queryset() if can_edit else None

    categories = OrderedDict(Ship.CATEGORY_CHOICES)
    categorized_ships = {code: [] for code in categories}

    for ship in ships:
        grouped_slots = OrderedDict()
        for slot in ship.role_slots.all():
            if can_edit:
                slot.form = RoleSlotForm(
                    instance=slot,
                    user_queryset=user_queryset,
                )
            slot.badge_class = STATUS_BADGES.get(slot.status, STATUS_BADGES["open"])
            grouped_slots.setdefault(slot.role_name, []).append(slot)
        ship.grouped_slots = list(grouped_slots.items())
        categorized_ships[ship.category].append(ship)

    grouped_ships = [
        (label, categorized_ships[code])
        for code, label in categories.items()
        if categorized_ships[code]
    ]

    return render(
        request,
        "ops/ship_allocation.html",
        {
            "can_edit": can_edit,
            "grouped_ships": grouped_ships,
        },
    )


@login_required
def ship_detail(request, pk):
    """Display the details of a single ship and manage its role templates."""

    ship = get_object_or_404(Ship, pk=pk)
    can_edit = is_planner(request.user)
    user_queryset = RoleSlotForm.default_user_queryset() if can_edit else None

    slots_by_role = defaultdict(list)
    for slot in ship.role_slots.select_related("user").order_by("role_name", "index"):
        if can_edit:
            slot.form = RoleSlotForm(
                instance=slot,
                user_queryset=user_queryset,
            )
        slot.badge_class = STATUS_BADGES.get(slot.status, STATUS_BADGES["open"])
        slots_by_role[slot.role_name].append(slot)

    role_form = ShipRoleTemplateForm()

    if request.method == "POST" and can_edit and "role_name" in request.POST:
        role_form = ShipRoleTemplateForm(request.POST)
        if role_form.is_valid():
            role_template = role_form.save(commit=False)
            role_template.ship = ship
            role_template.save()
            messages.success(request, "Rôle ajouté au vaisseau.")
            return redirect("ship_detail", pk=ship.pk)

    return render(
        request,
        "ops/ship_detail.html",
        {
            "ship": ship,
            "slots_by_role": dict(slots_by_role),
            "role_form": role_form,
            "can_edit": can_edit,
        },
    )


@login_required
@user_passes_test(is_planner)
def role_slot_update(request, pk):
    """Update a single role slot assignment."""

    slot = get_object_or_404(RoleSlot, pk=pk)

    if request.method == "POST":
        form = RoleSlotForm(
            request.POST,
            instance=slot,
            user_queryset=RoleSlotForm.default_user_queryset(),
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Affectation mise à jour.")
        next_url = request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)

    return redirect("ship_detail", pk=slot.ship_id)

