from django.contrib import admin

from .models import Ship, ShipRoleTemplate, RoleSlot
from .utils import resolve_username_lookup

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

    def get_search_fields(self, request):
        _, identifier = resolve_username_lookup()
        return ("ship__name", "role_name", f"user__{identifier}")
