from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from tasks.models import Task


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="senha123")
        self.client = Client()

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard-home"))
        self.assertNotEqual(response.status_code, 200)

    def test_dashboard_shows_pending_task(self):
        self.client.login(username="testuser", password="senha123")
        Task.objects.create(title="Tarefa visível no dashboard")
        response = self.client.get(reverse("dashboard-home"))
        self.assertContains(response, "Tarefa visível no dashboard")
        