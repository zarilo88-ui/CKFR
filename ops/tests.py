from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import Ship
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


class CurrentUrlNameTagTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def render_tag(self, path):
        request = self.factory.get(path)
        template = Template("{% load ops_extras %}{% current_url_name as name %}{{ name }}")
        return template.render(Context({"request": request}))

    def test_returns_resolved_url_name(self):
        rendered = self.render_tag(reverse("ships_list"))
        self.assertEqual(rendered, "ships_list")

    def test_returns_empty_string_when_resolution_fails(self):
        rendered = self.render_tag("/does-not-exist/")
        self.assertEqual(rendered, "")


class LayoutChromeTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user("nav", "nav@example.com", "pass")

    def test_login_page_hides_navigation_for_anonymous_users(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Déconnexion")

    def test_login_page_hides_navigation_for_authenticated_users(self):
        self.client.login(username="nav", password="pass")
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Déconnexion")

    def test_authenticated_users_see_navigation_on_application_pages(self):
        self.client.login(username="nav", password="pass")
        Ship.objects.create(name="Cetus", category="MR", min_crew=1, max_crew=4)
        response = self.client.get(reverse("ships_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Déconnexion")
