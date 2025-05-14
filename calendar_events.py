import os
import pickle
import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope for accessing Google Calendar data (read-only access)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Function to authenticate the user's Google account and return the Calendar API service
def authenticate_google_account():
    """
    Authenticates the user's Google account using OAuth2.0 and returns a Google Calendar API service object.
    It checks if there is an existing authentication token. If not, it prompts for authentication.
    """
    creds = None

    # Check if the token.pickle file exists, which stores the authentication token
    if os.path.exists('token.pickle'):
        # If the token exists, load it into creds
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If creds is None or expired, initiate a new authentication flow
    if not creds or not creds.valid:
        # Refresh the token if expired, otherwise prompt the user to authenticate
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Using InstalledAppFlow to handle the OAuth2 flow and store the credentials in creds
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the new credentials in token.pickle for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the Google Calendar API service using the authenticated credentials
    service = build('calendar', 'v3', credentials=creds)
    return service

# Function to fetch events from multiple Google Calendars and store them in a pandas DataFrame
def get_events_from_multiple_calendars(service, calendar_ids):
    """
    Fetches events from a list of Google Calendar IDs and stores the event details in a DataFrame.
    Each calendar's events are fetched separately and added to a combined DataFrame.
    """
    event_data = []

    # Loop through each calendar ID provided in calendar_ids list
    for calendar_id in calendar_ids:
        page_token = None
        while True:
            # Fetch events from the calendar with pagination (handling nextPageToken)
            events_result = service.events().list(
                calendarId=calendar_id, timeMin='2024-01-01T00:00:00Z', 
                maxResults=2500, singleEvents=True, orderBy='startTime',
                pageToken=page_token).execute()
            
            events = events_result.get('items', [])
            
            # If no events are found in a calendar, print a message
            if not events:
                print(f'No upcoming events found in calendar {calendar_id}.')
            
            # Loop through the events and extract necessary details
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))  # Start time of the event
                end = event['end'].get('dateTime', event['end'].get('date'))  # End time of the event
                
                # Get the attendees' emails, if any
                attendees = event.get('attendees', [])
                guest_list = ', '.join([attendee['email'] for attendee in attendees if 'email' in attendee])
                
                # Append the event details into the event_data list, including the event ID and created timestamp
                event_data.append({
                    'ID': event['id'],  # Event ID
                    'Calendar ID': calendar_id,
                    'Summary': event.get('summary', 'No summary available'),  # Use .get() to safely access 'summary'
                    'Start Time': start,
                    'End Time': end,
                    'Guests': guest_list,
                    'Created At': event.get('created', None)  # When the event was created
                })

            # Check if there's a nextPageToken to fetch the next page of results
            page_token = events_result.get('nextPageToken')
            if not page_token:
                break  # Break out of the loop if there's no nextPageToken

    # Convert the collected event data into a pandas DataFrame for easy manipulation
    df = pd.DataFrame(event_data)
    return df

# Function to authenticate and fetch event data from specified Google Calendars
def fetch_calendar_data():
    """
    Authenticates the Google account and fetches events from multiple Google Calendars.
    Returns a pandas DataFrame containing the event details.
    """
    # Authenticate and get the Google Calendar service
    service = authenticate_google_account()
    
    # Define the list of calendar IDs to fetch events from
    calendar_ids = [
        'user1@example.com',  # Your own calendar
        'user2@example.com',
        'user3@example.com',
        'user4@example.com',
        'user5@example.com',
        'user6@example.com',
        'user7@example.com',
        'user8@example.com',
        'user9@example.com',
        'user10@example.com',
        'user11@example.com',
        'user12@example.com',
        'user13@example.com'  # Another user's calendar    
    ]
    
    # Fetch events from multiple calendars and return the DataFrame
    df = get_events_from_multiple_calendars(service, calendar_ids)
    return df

# Now you can call the function to get event data as a DataFrame
if __name__ == '__main__':
    df = fetch_calendar_data()  # This will return the DataFrame, and you can access it outside the function
    
    # Convert the 'Created At' column to datetime objects for easier handling if needed
    if 'Created At' in df.columns:
        df['Created At'] = pd.to_datetime(df['Created At'])
    
    # Print the DataFrame to view the fetched events
    print(df)
