from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Task


class TaskModelTests(TestCase):
    def test_str_returns_title(self):
        task = Task.objects.create(title="Estudar física")
        self.assertEqual(str(task), "Estudar física")

    def test_default_status_is_pendente(self):
        task = Task.objects.create(title="Tarefa nova")
        self.assertEqual(task.status, "pendente")


class TaskViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="senha123")
        self.client = Client()
        self.client.login(username="testuser", password="senha123")

    def test_task_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("task-list"))
        self.assertNotEqual(response.status_code, 200)  # deve redirecionar pro login

    def test_task_list_shows_created_task(self):
        Task.objects.create(title="Revisar exercícios")
        response = self.client.get(reverse("task-list"))
        self.assertContains(response, "Revisar exercícios")

    def test_create_task_via_form(self):
        response = self.client.post(reverse("task-create"), {
            "title": "Nova tarefa de teste",
            "description": "",
            "due_date": "",
            "priority": "media",
            "status": "pendente",
        })
        self.assertEqual(response.status_code, 302)  # redireciona após salvar
        self.assertTrue(Task.objects.filter(title="Nova tarefa de teste").exists())

    def test_complete_task(self):
        task = Task.objects.create(title="Tarefa a concluir")
        self.client.get(reverse("task-complete", args=[task.pk]))
        task.refresh_from_db()
        self.assertEqual(task.status, "concluida")