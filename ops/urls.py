from django.urls import path
from . import views

urlpatterns = [
    path("operation/", views.operation_overview, name="operation_overview"),
    path("operations/manage/", views.operations_manage, name="operations_manage"),
    path("operations/<int:pk>/edit/", views.operation_edit, name="operation_edit"),
    path(
        "operations/<int:pk>/activate/",
        views.operation_activate,
        name="operation_activate",
    ),
    path("operations/<int:pk>/delete/", views.operation_delete, name="operation_delete"),
    path("ships/", views.ships_list, name="ships_list"),
    path("ships/allocation/", views.ships_allocation, name="ships_allocation"),
    path("ships/<int:pk>/", views.ship_detail, name="ship_detail"),
    path("slot/<int:pk>/update/", views.role_slot_update, name="role_slot_update"),
]