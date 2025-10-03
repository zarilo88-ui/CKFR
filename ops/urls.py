from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("ops/new/", views.operation_create, name="operation_create"),
    path("ops/<int:pk>/", views.operation_detail, name="operation_detail"),
    path("ops/<int:pk>/add-ship/", views.operation_add_ship, name="operation_add_ship"),
    path("assign/<int:pk>/", views.assignment_update, name="assignment_update"),
]
