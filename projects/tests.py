from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project
from users.models import User


class TeamFinderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            name="Test",
            surname="User",
            phone="+79001234567",
        )
        self.client = Client()

    def test_project_list_page(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)

    def test_register_and_login(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "New",
                "surname": "User",
                "email": "new@example.com",
                "password": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_create_project(self):
        self.client.login(username="test@example.com", password="testpass123")
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "Test Project",
                "description": "Description",
                "github_url": "",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name="Test Project")
        self.assertEqual(project.owner, self.user)
        self.assertTrue(project.participants.filter(pk=self.user.pk).exists())

    def test_toggle_favorite(self):
        project = Project.objects.create(
            name="Fav Project",
            owner=self.user,
            status="open",
        )
        self.client.login(username="test@example.com", password="testpass123")
        response = self.client.post(reverse("projects:toggle_favorite", args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["favorited"])
        self.assertTrue(self.user.favorites.filter(pk=project.pk).exists())
