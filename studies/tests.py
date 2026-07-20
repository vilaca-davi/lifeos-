from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from .models import Subject, Grade, StudyLog
from .views import calculate_streak


class GradeCalculationTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Física")

    def test_bimester_sum(self):
        Grade.objects.create(subject=self.subject, type="prova", value=8.0, bimester=1)
        Grade.objects.create(subject=self.subject, type="trabalho", value=1.5, bimester=1)
        total = self.subject.grades.filter(bimester=1).aggregate(
            total=__import__("django.db.models", fromlist=["Sum"]).Sum("value")
        )["total"]
        self.assertEqual(total, 9.5)


class StreakCalculationTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Matemática")

    def test_no_logs_gives_zero_streak(self):
        self.assertEqual(calculate_streak(), 0)

    def test_studied_today_gives_streak_of_one(self):
        StudyLog.objects.create(subject=self.subject, date=date.today(), minutes=25)
        self.assertEqual(calculate_streak(), 1)

    def test_consecutive_days_count_correctly(self):
        today = date.today()
        for i in range(3):
            StudyLog.objects.create(subject=self.subject, date=today - timedelta(days=i), minutes=25)
        self.assertEqual(calculate_streak(), 3)

    def test_gap_breaks_streak(self):
        today = date.today()
        StudyLog.objects.create(subject=self.subject, date=today, minutes=25)
        StudyLog.objects.create(subject=self.subject, date=today - timedelta(days=2), minutes=25)  # pula 1 dia
        self.assertEqual(calculate_streak(), 1)


class SubjectViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="senha123")
        self.client = Client()
        self.client.login(username="testuser", password="senha123")
        self.subject = Subject.objects.create(name="História")

    def test_subject_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("subject-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_subject_detail_shows_name(self):
        response = self.client.get(reverse("subject-detail", args=[self.subject.pk]))
        self.assertContains(response, "História")