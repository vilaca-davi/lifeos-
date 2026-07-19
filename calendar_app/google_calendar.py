import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone as dj_timezone
from django.utils.dateparse import parse_datetime, parse_date

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDENTIALS_FILE = "google_credentials.json"
TOKEN_FILE = "token.json"


def get_credentials():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return creds


def get_calendar_service():
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)


def import_events_from_google():
    from .models import CalendarEvent

    service = get_calendar_service()
    now = datetime.now(dt_timezone.utc).isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=100,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    google_events = events_result.get("items", [])

    imported = 0
    for g_event in google_events:
        external_id = g_event["id"]
        title = g_event.get("summary", "(sem título)")
        description = g_event.get("description", "")
        is_recurring_instance = bool(g_event.get("recurringEventId"))

        start_raw = g_event["start"].get("dateTime", g_event["start"].get("date"))
        end_raw = g_event["end"].get("dateTime", g_event["end"].get("date"))

        start_dt = parse_datetime(start_raw) or parse_date(start_raw)
        end_dt = parse_datetime(end_raw) or parse_date(end_raw)

        if start_dt and dj_timezone.is_naive(start_dt) is False:
            pass  # já tem timezone (evento com horário)

        CalendarEvent.objects.update_or_create(
            external_id=external_id,
            defaults={
                "title": title,
                "description": description,
                "start_datetime": start_dt,
                "end_datetime": end_dt,
                "source": "google",
                "show_in_upcoming": not is_recurring_instance,
            },
        )
        imported += 1

    return imported


def export_event_to_google(event):
    from .models import CalendarEvent

    service = get_calendar_service()

    body = {
        "summary": event.title,
        "description": event.description,
        "start": {"dateTime": event.start_datetime.isoformat()},
        "end": {"dateTime": (event.end_datetime or event.start_datetime).isoformat()},
    }

    if event.external_id:
        result = service.events().update(
            calendarId="primary", eventId=event.external_id, body=body
        ).execute()
    else:
        result = service.events().insert(calendarId="primary", body=body).execute()
        event.external_id = result["id"]
        event.source = "manual"
        event.save(update_fields=["external_id"])

    return result