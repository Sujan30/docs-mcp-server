from authentication import authenticate, CREDENTIALS_FILE, TOKEN_FILE
import datetime
import os.path


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError




class calendar:
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

        


if __name__ == "__main__":
  calendar.main()