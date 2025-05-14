import os
import pickle
import pandas as pd
import psycopg2
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from psycopg2.extras import execute_batch
from datetime import datetime

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

# Function to parse datetime strings that could be in various formats
def parse_datetime_safely(dt_str):
    """
    Safely parse datetime strings that could be in different formats.
    Handles both full ISO format with time and date-only format.
    """
    if not dt_str:
        return None
    
    try:
        # Check if it's a date-only string (YYYY-MM-DD)
        if len(dt_str) == 10 and dt_str[4] == '-' and dt_str[7] == '-':
            return datetime.strptime(dt_str, '%Y-%m-%d')
        
        # For full ISO format with timezone
        return pd.to_datetime(dt_str)
    except Exception as e:
        print(f"Warning: Could not parse datetime '{dt_str}': {e}")
        return None

# Function to insert DataFrame rows into PostgreSQL
def insert_df_to_postgres(df):
    """
    Inserts the DataFrame rows into the PostgreSQL table.
    """
    # Database connection parameters
    host = "your-db-host.example.com"
    port = 5432
    database = "your_database_name"
    user = "your_username"
    password = "your_password"
    
    try:
        # Establish connection to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        print("✅ Connected successfully!")
        
        # Create a cursor
        cur = conn.cursor()
        
        # Prepare the data for insertion
        # Make sure column names match between DataFrame and PostgreSQL table
        insert_query = '''
        INSERT INTO google_calendar.calendar_events 
        (id, calendar_id, summary, start_time, end_time, guests, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        
        # Convert DataFrame to list of tuples for batch insertion
        data_tuples = []
        for _, row in df.iterrows():
            # Parse the datetime strings safely
            start_time = parse_datetime_safely(row['Start Time'])
            end_time = parse_datetime_safely(row['End Time'])
            created_at = parse_datetime_safely(row['Created At']) if pd.notna(row['Created At']) else None
            
            data_tuples.append((
                row['ID'],
                row['Calendar ID'],
                row['Summary'],
                start_time,
                end_time,
                row['Guests'],
                created_at
            ))
        
        # Use execute_batch for efficient insertion of multiple rows
        execute_batch(cur, insert_query, data_tuples, page_size=100)
        
        # Commit the transaction
        conn.commit()
        print(f"✅ Successfully inserted {len(data_tuples)} rows into the database!")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database operation failed: {e}")

# Now let's fetch the data and insert it into PostgreSQL
if __name__ == '__main__':
    # Fetch calendar data
    df = fetch_calendar_data()
    
    # Print preview of the DataFrame
    print("Preview of the DataFrame:")
    print(df.head())
    print(f"Total rows: {len(df)}")
    
    # Insert the data into PostgreSQL
    insert_df_to_postgres(df)
