from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.
from .utils import get_ordered_user_queryset, resolve_username_lookup


class UserOrderingUtilsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.original_username_field = getattr(cls.User, "USERNAME_FIELD", "username")
        # Create users with intentionally unordered identifiers.
        cls.u1 = cls.User.objects.create_user(username="zoe", password="pass", email="zoe@example.com")
        cls.u2 = cls.User.objects.create_user(username="anna", password="pass", email="anna@example.com")
        cls.u3 = cls.User.objects.create_user(username="mike", password="pass", email="mike@example.com")

    def tearDown(self):
        # Restore the USERNAME_FIELD if tests changed it.
        self.User.USERNAME_FIELD = self.original_username_field

    def test_resolve_username_lookup_returns_configured_field(self):
        _, field_name = resolve_username_lookup()
        self.assertEqual(field_name, self.original_username_field)

    def test_resolve_username_lookup_falls_back_to_pk(self):
        self.User.USERNAME_FIELD = "nonexistent_field"
        _, field_name = resolve_username_lookup()
        self.assertEqual(field_name, "pk")

    def test_get_ordered_queryset_falls_back_to_pk(self):
        self.User.USERNAME_FIELD = "nonexistent_field"
        ordered_ids = list(get_ordered_user_queryset().values_list("pk", flat=True))
        expected_ids = list(self.User._default_manager.order_by("pk").values_list("pk", flat=True))
        self.assertEqual(ordered_ids, expected_ids)