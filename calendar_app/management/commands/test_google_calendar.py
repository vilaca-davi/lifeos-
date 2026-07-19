from django.core.management.base import BaseCommand
from calendar_app.google_calendar import get_calendar_service


class Command(BaseCommand):
    help = "Testa a conexão com o Google Calendar listando os próximos eventos"

    def handle(self, *args, **options):
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId="primary",
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = events_result.get("items", [])

        if not events:
            self.stdout.write("Nenhum evento encontrado no Google Agenda.")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            self.stdout.write(f"{start} — {event.get('summary', '(sem título)')}")