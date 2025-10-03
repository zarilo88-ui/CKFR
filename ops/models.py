# ops/models.py (ajoute Meta pour chaque modèle)

class Ship(models.Model):
    name = models.CharField(max_length=80, unique=True)
    min_crew = models.PositiveSmallIntegerField(default=1)
    max_crew = models.PositiveSmallIntegerField()
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Vaisseau"
        verbose_name_plural = "Vaisseaux"

class ShipRoleTemplate(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name="roles")
    role_name = models.CharField(max_length=40)
    slots = models.PositiveSmallIntegerField(default=1)
    class Meta:
        unique_together = ("ship", "role_name")
        verbose_name = "Rôle (modèle)"
        verbose_name_plural = "Rôles (modèles)"
    def __str__(self): return f"{self.ship} · {self.role_name} x{self.slots}"

class Operation(models.Model):
    title = models.CharField(max_length=120)
    start = models.DateTimeField()
    description = models.TextField(blank=True)
    def __str__(self): return f"{self.title} @ {self.start:%Y-%m-%d %H:%M}"
    class Meta:
        verbose_name = "Opération"
        verbose_name_plural = "Opérations"

class OperationShip(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name="ships")
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    def __str__(self): return f"{self.operation} · {self.ship}"
    class Meta:
        verbose_name = "Vaisseau d’opération"
        verbose_name_plural = "Vaisseaux d’opération"

class Assignment(models.Model):
    operation_ship = models.ForeignKey(OperationShip, on_delete=models.CASCADE, related_name="assignments")
    role_name = models.CharField(max_length=40)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=16, default="open",
                              choices=[("open","Ouvert"),("assigned","Assigné"),("confirmed","Confirmé")])
    def __str__(self): return f"{self.operation_ship} · {self.role_name} → {self.user or 'libre'}"
    class Meta:
        verbose_name = "Affectation"
        verbose_name_plural = "Affectations"