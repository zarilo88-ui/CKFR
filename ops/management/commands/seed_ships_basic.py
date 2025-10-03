from django.core.management.base import BaseCommand
from ops.models import Ship, ShipRoleTemplate

STARTERS = [
    ("Anvil Arrow", "LF"), ("Aegis Gladius", "LF"), ("Anvil Hawk", "LF"),
    ("Origin 125a", "LF"), ("Consolidated Outland Mustang Delta", "LF"),
    ("Aopoa Khartu-al", "LF"), ("MISC Reliant Tana", "LF"), ("Esperia Talon", "LF"),
    ("Aegis Sabre", "MF"), ("Aegis Sabre Comet", "MF"), ("Banu Defender", "MF"),
    ("Anvil F7C Hornet Mk I", "MF"), ("Anvil F7C-M Super Hornet Mk I", "MF"),
    ("Anvil Hurricane", "HF"), ("RSI Scorpius", "HF"), ("RSI Scorpius Antares", "HF"),
    ("Crusader Ares Inferno", "HF"), ("Crusader Ares Ion", "HF"), ("Anvil F8C Lightning", "HF"),
    ("Drake Cutlass Black", "MR"), ("Aegis Avenger Titan", "MR"), ("MISC Freelancer MIS", "MR"),
    ("RSI Polaris", "CAP"), ("Aegis Idris-P", "CAP"),
]

CATEGORY_ROLES = {
    "LF": [("Pilote", 1)],
    "MF": [("Pilote", 1)],
    "HF": [("Pilote", 1), ("Artilleur", 1)],
    "MR": [("Pilote", 1), ("Artilleur", 1)],
    "CAP": [("Commandant", 1), ("Pilote", 1), ("Navigateur", 1), ("Ingénierie", 2), ("Artilleur", 4)],
}

class Command(BaseCommand):
    help = "Seed minimal ship list with categories and generic role templates."
    def handle(self, *args, **kwargs):
        for name, cat in STARTERS:
            ship, _ = Ship.objects.get_or_create(name=name, defaults={"category": cat, "min_crew": 1, "max_crew": 2})
            if ship.category != cat:
                ship.category = cat
                ship.save(update_fields=["category"])
            if ship.role_templates.count() == 0:
                for role, slots in CATEGORY_ROLES.get(cat, [("Pilote",1)]):
                    ShipRoleTemplate.objects.get_or_create(ship=ship, role_name=role, defaults={"slots": slots})
        self.stdout.write(self.style.SUCCESS("Seed complete."))
