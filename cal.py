from authentication import authenticate, CREDENTIALS_FILE, TOKEN_FILE
import datetime
import os.path


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarClient:
    def __init__(self):
        self.creds = authenticate()
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    # return the next x # of events
    def GetEvents(self , num : int):
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        try:
            events_result = (
        self.service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
            events = events_result.get('items', [])
            if not events:
                print("No upcoming events found.")
                return
        
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event["summary"])
        
        except HttpError as error:
            print(f"An error occurred: {error}")
    

    
    def createEvent(self, summary, description, start_iso, end_iso=None, calendar_id="primary", user_tz="UTC"):
        """
        Create a Google Calendar event using exactly the user's IANA timezone (user_tz).
        - `start_iso` and `end_iso` must already be full ISO‐8601 strings with offset (e.g. "2025-06-02T17:00:00+02:00").
        - `user_tz` is something like "Europe/Paris" or "America/Los_Angeles".
        """
        global service, creds

        # Ensure credentials exist
        if creds is None:
            authenticate()

        if service is None and creds is not None:
            self.service = build("calendar", "v3", credentials=creds)

        if not summary or not start_iso:
            print("Missing required parameters for createEvent")
            return False

        try:
            # Now that ChatGPT has given us a full ISO‐8601 with offset in start_iso,
        # we can parse it into a tz-aware datetime:
            start_dt = datetime.datetime.fromisoformat(start_iso)
            # If end_iso is omitted, default to 1 hour after:
            if not end_iso or end_iso == "":
                end_dt = start_dt + datetime.timedelta(hours=1)
                end_iso = end_dt.isoformat()
            else:
                end_dt = datetime.datetime.fromisoformat(end_iso)

            if end_dt <= start_dt:
              print("Error: End time must be after start time")
              return False

        except ValueError as e:
            print(f"Invalid datetime format: {e}")
            return False

    # Use the USER’S timezone (user_tz), not server’s. Do NOT compute server‐side tz anymore.
        event_body = {
        "summary": summary,
        "description": description or "",
        "start": {
            "dateTime": start_iso,   # e.g. "2025-06-02T17:00:00+02:00"
            "timeZone": user_tz,     # e.g. "Europe/Paris"
        },
        "end": {
            "dateTime": end_iso,
            "timeZone": user_tz,
        },
    }
        try:
            event = self.service.events().insert(calendarId = 'primary', body=event_body)
            print (f'Event created: %s' % (event.get('htmlLink')))
            return True
        except Exception as e:
            print(f'error creating event {e}')
            return False

        


