from django.urls import path
from . import views

urlpatterns = [
    path("", views.ships_list, name="ships_list"),
    path("ship/<int:pk>/", views.ship_detail, name="ship_detail"),
    path("slot/<int:pk>/update/", views.role_slot_update, name="role_slot_update"),
]
