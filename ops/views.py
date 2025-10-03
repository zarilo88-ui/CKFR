from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Operation, OperationShip, Assignment
from .forms import OperationForm, OperationShipForm, AssignmentForm

def is_planner(user):
    return user.is_superuser or user.groups.filter(name__in=["Planner","Admin"]).exists()

@login_required
def dashboard(request):
    ops = Operation.objects.order_by("start")[:20]
    return render(request, "ops/operation_list.html", {"ops": ops})

@login_required
@user_passes_test(is_planner)
def operation_create(request):
    if request.method == "POST":
        form = OperationForm(request.POST)
        if form.is_valid():
            op = form.save()
            messages.success(request, "Operation created.")
            return redirect("operation_detail", pk=op.pk)
    else:
        form = OperationForm()
    return render(request, "ops/operation_form.html", {"form": form})

@login_required
def operation_detail(request, pk):
    op = get_object_or_404(Operation, pk=pk)
    ships = op.ships.select_related("ship").prefetch_related("assignments__user")
    return render(request, "ops/operation_detail.html", {"op": op, "ships": ships, "ship_form": OperationShipForm()})

@login_required
@user_passes_test(is_planner)
def operation_add_ship(request, pk):
    op = get_object_or_404(Operation, pk=pk)
    if request.method == "POST":
        form = OperationShipForm(request.POST)
        if form.is_valid():
            os = form.save(commit=False)
            os.operation = op
            os.save()  # seeds assignments via signal
            messages.success(request, "Ship added to operation.")
    return redirect("operation_detail", pk=pk)

@login_required
@user_passes_test(is_planner)
def assignment_update(request, pk):
    a = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated.")
    return redirect("operation_detail", pk=a.operation_ship.operation_id)