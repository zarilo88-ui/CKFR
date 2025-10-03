from django.contrib import admin
from .models import Ship, ShipRoleTemplate, RoleSlot

class ShipRoleTemplateInline(admin.TabularInline):
    model = ShipRoleTemplate
    extra = 1

@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "min_crew", "max_crew")
    list_filter = ("category",)
    search_fields = ("name",)
    inlines = [ShipRoleTemplateInline]

@admin.register(RoleSlot)
class RoleSlotAdmin(admin.ModelAdmin):
    list_display = ("ship", "role_name", "index", "user", "status")
    list_filter = ("ship", "role_name", "status")
    search_fields = ("ship__name", "role_name", "user__username")
