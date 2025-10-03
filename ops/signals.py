from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OperationShip, Assignment

@receiver(post_save, sender=OperationShip)
def seed_slots(sender, instance, created, **kwargs):
    if created:
        for rt in instance.ship.roles.all():
            for _ in range(rt.slots):
                Assignment.objects.create(operation_ship=instance, role_name=rt.role_name)
