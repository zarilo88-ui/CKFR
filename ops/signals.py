from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ShipRoleTemplate, RoleSlot

def _ensure_slots_for_template(rt: ShipRoleTemplate):
    existing = set(RoleSlot.objects.filter(ship=rt.ship, role_name=rt.role_name).values_list("index", flat=True))
    for idx in range(1, rt.slots + 1):
        if idx not in existing:
            RoleSlot.objects.create(ship=rt.ship, role_name=rt.role_name, index=idx)

@receiver(post_save, sender=ShipRoleTemplate)
def template_saved(sender, instance, created, **kwargs):
    _ensure_slots_for_template(instance)

@receiver(post_delete, sender=ShipRoleTemplate)
def template_deleted(sender, instance, **kwargs):
    # No automatic deletion of RoleSlot to avoid losing assignments
    pass
