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
    def GetEvents(self, num: int):
        """
    Get the next 'num' upcoming events from the primary calendar.
    
    Args:
        num (int): Number of events to retrieve
        
    Returns:
        list: List of event dictionaries, or empty list if no events found
    """
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    
        try:
            events_result = (
                self.service.events()
                .list(
                calendarId="primary",
                timeMin=now,
                maxResults=num,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        
            events = events_result.get('items', [])
        
            if not events:
                print("No upcoming events found.")
                return 'no upcoming events found'
        
            # Print events for debugging/display purposes
            print(f"Found {len(events)} upcoming event(s):")
            for i, event in enumerate(events, 1):
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"{i}. {start} - {event['summary']}")
        
            # Return the events list so it can be used by other functions
            return events
        
        except HttpError as error:
            print(f"An error occurred: {error}")
            return 'error fetching events'
    



    def createEvent(self, event: dict):
        """
    Create a Google Calendar event using the provided event dictionary.
    
    Args:
        event (dict): Event dictionary containing all event details including:
            - summary (required): Event title
            - start (required): Dict with 'dateTime' and 'timeZone'
            - end (required): Dict with 'dateTime' and 'timeZone'
            - description (optional): Event description
            - location (optional): Event location
            - attendees (optional): List of attendee dicts with 'email'
            - recurrence (optional): List of recurrence rules
            - reminders (optional): Dict with reminder settings
    
    Returns:
        bool: True if event created successfully, False otherwise
    """

        # Ensure credentials exist
        if self.creds is None:
            self.creds = authenticate()

        if self.service is None and self.creds is not None:
            self.service = build("calendar", "v3", credentials=self.creds)

    # Validate required fields
        if not event.get('summary'):
            print("Missing required parameter: summary")
            return False
    
        if not event.get('start') or not event.get('start', {}).get('dateTime'):
            print("Missing required parameter: start.dateTime")
            return False
    
        if not event.get('end') or not event.get('end', {}).get('dateTime'):
            print("Missing required parameter: end.dateTime")
            return False

        try:
            # Validate datetime formats
            start_iso = event['start']['dateTime']
            end_iso = event['end']['dateTime']
        
            start_dt = datetime.datetime.fromisoformat(start_iso)
            end_dt = datetime.datetime.fromisoformat(end_iso)

            if end_dt <= start_dt:
                print("Error: End time must be after start time")
                return False

        except ValueError as e:
            print(f"Invalid datetime format: {e}")
            return False


    # Build the event body with all provided fields
        event_body = {
        "summary": event['summary'],
        "start": {
            "dateTime": event['start']['dateTime'],
            "timeZone": event['start'].get('timeZone', 'UTC'),
        },
        "end": {
            "dateTime": event['end']['dateTime'],
            "timeZone": event['end'].get('timeZone', 'UTC'),
        },
    }
    
    # Add optional fields if provided
        if event.get('description'):
            event_body['description'] = event['description']
    
        if event.get('location'):
            event_body['location'] = event['location']

        if event.get('attendees'):
            event_body['attendees'] = event['attendees']
    
        if event.get('recurrence'):
            event_body['recurrence'] = event['recurrence']
    
        if event.get('reminders'):
            event_body['reminders'] = event['reminders']

        try:
            result = self.service.events().insert(calendarId='primary', body=event_body).execute()
            print(f'Event created: {result.get("htmlLink")}')
            return result.get("htmlLink")
        except Exception as e:
            print(f'Error creating event: {e}')
            return 'error creating the new calendar event'