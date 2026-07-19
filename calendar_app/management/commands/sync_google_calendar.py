from django.core.management.base import BaseCommand
from calendar_app.google_calendar import import_events_from_google


class Command(BaseCommand):
    help = "Importa eventos do Google Agenda para o LifeOS"

    def handle(self, *args, **options):
        count = import_events_from_google()
        self.stdout.write(self.style.SUCCESS(f"{count} evento(s) importado(s)/atualizado(s)."))