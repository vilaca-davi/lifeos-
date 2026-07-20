from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import CalendarEvent
from .utils import get_occurrences


class RecurringEventTests(TestCase):
    def test_weekly_recurrence_generates_multiple_occurrences(self):
        start = timezone.now()
        event = CalendarEvent.objects.create(
            title="Treino",
            start_datetime=start,
            is_recurring=True,
            recurrence_rule="FREQ=WEEKLY;COUNT=4",
            show_in_upcoming=False,
        )
        range_start = start - timedelta(minutes=1)  # margem de segurança contra precisão de microssegundos
        range_end = start + timedelta(weeks=6)
        occurrences = get_occurrences(event, range_start, range_end)
        self.assertEqual(len(occurrences), 4)

    def test_non_recurring_event_returns_single_occurrence(self):
        start = timezone.now()
        event = CalendarEvent.objects.create(title="Consulta", start_datetime=start)
        range_end = start + timedelta(days=1)
        occurrences = get_occurrences(event, start, range_end)
        self.assertEqual(len(occurrences), 1)

    def test_recurring_event_defaults_hidden_from_upcoming(self):
        event = CalendarEvent.objects.create(
            title="Aula semanal",
            start_datetime=timezone.now(),
            is_recurring=True,
            recurrence_rule="FREQ=WEEKLY",
            show_in_upcoming=False,
        )
        self.assertFalse(event.show_in_upcoming)