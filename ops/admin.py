from django.contrib import admin
from .models import Ship, ShipRoleTemplate, Operation, OperationShip, Assignment

class ShipRoleTemplateInline(admin.TabularInline):
    model = ShipRoleTemplate
    extra = 1

@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ("name","min_crew","max_crew")
    inlines = [ShipRoleTemplateInline]

class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    readonly_fields = ("role_name",)

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ("title","start")
    search_fields = ("title",)
    date_hierarchy = "start"

@admin.register(OperationShip)
class OperationShipAdmin(admin.ModelAdmin):
    list_display = ("operation","ship")
    inlines = [AssignmentInline]