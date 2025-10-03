from django.db import models
from django.contrib.auth.models import User

class Ship(models.Model):
    name = models.CharField("Nom du vaisseau", max_length=80, unique=True)
    CATEGORY_CHOICES = [
        ("LF", "Chasseur léger"),
        ("MF", "Chasseur moyen"),
        ("HF", "Chasseur lourd"),
        ("MR", "Multirôle"),
        ("CAP", "Capital"),
    ]
    category = models.CharField("Catégorie", max_length=3, choices=CATEGORY_CHOICES, default="MR")
    min_crew = models.PositiveSmallIntegerField("Équipage minimum", default=1)
    max_crew = models.PositiveSmallIntegerField("Équipage maximum")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vaisseau"
        verbose_name_plural = "Vaisseaux"

class ShipRoleTemplate(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name="role_templates", verbose_name="Vaisseau")
    role_name = models.CharField("Rôle", max_length=40)
    slots = models.PositiveSmallIntegerField("Nombre de places", default=1)

    class Meta:
        unique_together = ("ship", "role_name")
        verbose_name = "Rôle (modèle)"
        verbose_name_plural = "Rôles (modèles)"

    def __str__(self):
        return f"{self.ship} · {self.role_name} ×{self.slots}"

class RoleSlot(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name="role_slots", verbose_name="Vaisseau")
    role_name = models.CharField("Rôle", max_length=40)
    index = models.PositiveSmallIntegerField("N° de place", default=1)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Utilisateur")
    status = models.CharField(
        "Statut",
        max_length=16,
        default="open",
        choices=[("open", "Libre"), ("assigned", "Assigné"), ("confirmed", "Confirmé")],
    )

    class Meta:
        unique_together = ("ship", "role_name", "index")
        verbose_name = "Place de rôle"
        verbose_name_plural = "Places de rôle"

    def __str__(self):
        who = self.user.username if self.user else "libre"
        return f"{self.ship} · {self.role_name} #{self.index} → {who}"
