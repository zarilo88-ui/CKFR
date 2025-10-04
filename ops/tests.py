from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import RoleSlot, Ship
from .utils import get_ordered_user_queryset, resolve_username_lookup


class UserOrderingUtilsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.original_username_field = getattr(cls.User, "USERNAME_FIELD", "username")
        # Create users with intentionally unordered identifiers.
        cls.User.objects.create_user(username="zoe", password="pass", email="zoe@example.com")
        cls.User.objects.create_user(username="anna", password="pass", email="anna@example.com")
        cls.User.objects.create_user(username="mike", password="pass", email="mike@example.com")

    def tearDown(self):
        # Restore the USERNAME_FIELD if tests changed it.
        self.User.USERNAME_FIELD = self.original_username_field

    def test_resolve_username_lookup_returns_configured_field(self):
        _, field_name = resolve_username_lookup()
        self.assertEqual(field_name, self.original_username_field)

    def test_resolve_username_lookup_falls_back_to_pk(self):
@@ -54,25 +56,49 @@ class RoleSlotUpdateViewTests(TestCase):
            min_crew=1,
            max_crew=4,
        )
        cls.slot = RoleSlot.objects.create(
            ship=cls.ship,
            role_name="Pilote",
            index=1,
            status="open",
        )

    def test_redirects_to_safe_next_url(self):
        self.client.force_login(self.planner)
        response = self.client.post(
            reverse("role_slot_update", args=[self.slot.pk]),
            {
                "user": "",
                "status": "open",
                "next": "/ops/ships/allocation/",
            },
        )
        self.assertRedirects(
            response,
            "/ops/ships/allocation/",
            fetch_redirect_response=False,
        )


class SourceConflictMarkerTests(SimpleTestCase):
    def test_python_sources_do_not_contain_conflict_markers(self):
        root = Path(__file__).resolve().parent.parent
        this_file = Path(__file__).resolve()
        excluded = {".git", "__pycache__", ".venv"}
        markers = ("<<<<<<<", "=======", ">>>>>>>", "@@ -")

        for path in root.rglob("*.py"):
            if path.resolve() == this_file:
                continue

            if any(part in excluded for part in path.parts):
                continue

            text = path.read_text(encoding="utf-8", errors="ignore")

            for marker in markers:
                self.assertNotIn(
                    marker,
                    text,
                    msg=f"Conflict marker '{marker}' found in {path.relative_to(root)}",
                )