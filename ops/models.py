from django.conf import settings
from django.db import models


class Operation(models.Model):
    """Represents a planned operation and its highlighted ships."""

    title = models.CharField("Nom de l'opération", max_length=120)
    description = models.TextField("Description", blank=True)
    is_active = models.BooleanField("Opération actuelle", default=False)
    highlighted_ships = models.ManyToManyField(
        "Ship",
        through="OperationHighlightedShip",
        related_name="highlighted_in_operations",
        blank=True,
        verbose_name="Vaisseaux mis en avant",
    )
    updated_at = models.DateTimeField("Mise à jour", auto_now=True)

    class Meta:
        verbose_name = "Opération"
        verbose_name_plural = "Opérations"

    def save(self, *args, **kwargs):
        if self.is_active:
            Operation.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


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
        """Return a human-readable crew range for display templates."""

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
    """Represents an individual assignable seat for a given ship role."""

    STATUS_CHOICES = [
        ("open", "Libre"),
        ("assigned", "Assigné"),
        ("confirmed", "Confirmé"),
    ]

    ship = models.ForeignKey(
        Ship,
        on_delete=models.CASCADE,
        related_name="role_slots",
        verbose_name="Vaisseau",
        )
    role_name = models.CharField("Rôle", max_length=40)
    index = models.PositiveSmallIntegerField("N° de place", default=1)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_slots",
        verbose_name="Utilisateur",
    )
    status = models.CharField(
        "Statut",
        max_length=16,
        default="open",
        choices=STATUS_CHOICES,
    )

    class Meta:
        unique_together = ("ship", "role_name", "index")
        verbose_name = "Place de rôle"
        verbose_name_plural = "Places de rôle"

    def __str__(self):
        who = self.user.get_username() if self.user else "libre"
        return f"{self.ship} · {self.role_name} #{self.index} → {who}"


class OperationHighlightedShip(models.Model):
    """Additional information for highlighted ships within an operation."""

    ROLE_CHOICES = [
        ("gunner", "Gunner"),
        ("infantry", "À pied"),
        ("pilot", "Pilote"),
        ("torpedo", "Torpille"),
    ]

    operation = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name="highlighted_ship_links",
        verbose_name="Opération",
    )
    ship = models.ForeignKey(
        Ship,
        on_delete=models.CASCADE,
        related_name="highlighted_operation_links",
        verbose_name="Vaisseau",
    )

    class Meta:
        unique_together = ("operation", "ship")
        verbose_name = "Vaisseau mis en avant"
        verbose_name_plural = "Vaisseaux mis en avant"

    def __str__(self) -> str:
        return f"{self.operation} · {self.ship}"

    @classmethod
    def get_role_label(cls, role: str) -> str:
        return dict(cls.ROLE_CHOICES).get(role, role)

    @property
    def crew_groups(self) -> dict[str, list[str]]:
        """Return cached crew assignments grouped by role."""

        if not hasattr(self, "_crew_by_role_cache"):
            grouped: dict[str, list[str]] = {role: [] for role, _ in self.ROLE_CHOICES}
            for assignment in self.crew_assignments.all():
                grouped.setdefault(assignment.role, []).append(assignment.crew_name)
            self._crew_by_role_cache = grouped
        return self._crew_by_role_cache

    def get_crew_list(self, role: str) -> list[str]:
        """Return the list of crew names assigned to a role."""

        return list(self.crew_groups.get(role, []))

    @property
    def role_rows(self) -> list[tuple[str, str, list[str]]]:
        """Return role metadata with associated crew lists for templating."""

        return [
            (role, label, self.get_crew_list(role))
            for role, label in self.ROLE_CHOICES
        ]


class OperationHighlightedCrewAssignment(models.Model):
    """Represents a named crew assignment for a highlighted ship role."""

    highlighted_ship = models.ForeignKey(
        OperationHighlightedShip,
        on_delete=models.CASCADE,
        related_name="crew_assignments",
        verbose_name="Vaisseau mis en avant",
    )
    role = models.CharField(
        "Rôle",
        max_length=16,
        choices=OperationHighlightedShip.ROLE_CHOICES,
    )
    crew_name = models.CharField("Membre d’équipage", max_length=120)
    order = models.PositiveSmallIntegerField("Ordre", default=1)

    class Meta:
        ordering = ("highlighted_ship", "role", "order", "id")
        verbose_name = "Assignation de rôle"
        verbose_name_plural = "Assignations de rôle"

    def __str__(self) -> str:
        role_label = OperationHighlightedShip.get_role_label(self.role)
        return f"{self.highlighted_ship} · {role_label} → {self.crew_name}"