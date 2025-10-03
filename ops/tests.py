from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

# Create your tests here.
from .models import RoleSlot, Ship


class ShipAllocationViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.planner = User.objects.create_user("planner", password="pw")
        cls.planner.is_superuser = True
        cls.planner.save()

        cls.viewer = User.objects.create_user("viewer", password="pw")
        cls.assignee = User.objects.create_user("ace", password="pw")

        cls.ship = Ship.objects.create(
            name="Corsair",
            category="MF",
            min_crew=1,
            max_crew=3,
        )
        cls.slot_open = RoleSlot.objects.create(
            ship=cls.ship,
            role_name="Pilote",
            index=1,
            status="open",
        )
        cls.slot_assigned = RoleSlot.objects.create(
            ship=cls.ship,
            role_name="Pilote",
            index=2,
            user=cls.assignee,
            status="assigned",
        )

    def test_planner_sees_editable_forms(self):
        self.client.force_login(self.planner)

        response = self.client.get(reverse("ships_allocation"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["can_edit"])

        grouped_ships = response.context["grouped_ships"]
        self.assertEqual(len(grouped_ships), 1)

        category_label, ships = grouped_ships[0]
        self.assertEqual(category_label, "Chasseur moyen")
        self.assertEqual(len(ships), 1)

        ship_context = ships[0]
        role_name, slots = list(ship_context.grouped_slots)[0]
        self.assertEqual(role_name, "Pilote")
        self.assertEqual(len(slots), 2)
        self.assertTrue(hasattr(slots[0], "form"))
        self.assertEqual(slots[0].form.instance, slots[0])

    def test_viewer_sees_read_only_allocation(self):
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("ships_allocation"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_edit"])

        grouped_ships = response.context["grouped_ships"]
        ship_context = grouped_ships[0][1][0]
        slots = list(ship_context.grouped_slots)[0][1]
        self.assertFalse(hasattr(slots[0], "form"))
        self.assertContains(response, self.assignee.username)

    def test_planner_can_update_role_slot(self):
        self.client.force_login(self.planner)
        url = reverse("role_slot_update", args=[self.slot_open.pk])
        next_url = reverse("ships_allocation")

        response = self.client.post(
            url,
            {
                "user": self.assignee.pk,
                "status": "confirmed",
                "next": next_url,
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], next_url)

        self.slot_open.refresh_from_db()
        self.assertEqual(self.slot_open.user, self.assignee)
        self.assertEqual(self.slot_open.status, "confirmed")