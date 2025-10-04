from django.conf import settings
from django.db import models


class Ship(models.Model):
    name = models.CharField("Nom du vaisseau", max_length=120, unique=True)
    manufacturer = models.CharField("Constructeur", max_length=80, blank=True)
    role = models.CharField("Type", max_length=120, blank=True)
    cargo_capacity = models.CharField("Soute (SCU)", max_length=32, blank=True)
    CATEGORY_CHOICES = [
        ("LF", "Chasseur léger"),
        ("MF", "Chasseur moyen"),
        ("HF", "Chasseur lourd"),
        ("MR", "Multirôle"),
        ("CAP", "Capital"),
    ]
    category = models.CharField(
        "Catégorie",
        max_length=3,
        choices=CATEGORY_CHOICES,
        default="MR",
    )
    min_crew = models.PositiveSmallIntegerField("Équipage minimum", default=1)
    max_crew = models.PositiveSmallIntegerField("Équipage maximum")

    def __str__(self):
        return self.name

    @property
    def crew_range_display(self) -> str:
        """Return a human readable crew range."""

        if self.min_crew == self.max_crew:
            return str(self.min_crew)
        return f"{self.min_crew}–{self.max_crew}"

    class Meta:
        verbose_name = "Vaisseau"
        verbose_name_plural = "Vaisseaux"


class ShipRoleTemplate(models.Model):
    ship = models.ForeignKey(
        Ship,
        on_delete=models.CASCADE,
        related_name="role_templates",
        verbose_name="Vaisseau",
    )
    role_name = models.CharField("Rôle", max_length=40)
    slots = models.PositiveSmallIntegerField("Nombre de places", default=1)

    class Meta:
        unique_together = ("ship", "role_name")
        verbose_name = "Rôle (modèle)"
        verbose_name_plural = "Rôles (modèles)"

    def __str__(self):
        return f"{self.ship} · {self.role_name} ×{self.slots}"


class RoleSlot(models.Model):