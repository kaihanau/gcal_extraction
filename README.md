# Google Calendar Events Fetcher

A lightweight Python utility for fetching events from multiple Google Calendars and exporting them as a pandas DataFrame.

## Overview

This tool provides a simpler implementation to:
1. Authenticate with Google Calendar API
2. Fetch events from multiple Google Calendars
3. Format the data into a pandas DataFrame for further analysis

## Features

- OAuth 2.0 authentication with Google APIs
- Support for retrieving events from multiple calendars
- Pagination for handling large numbers of events
- Comprehensive event data including:
  - Event ID and summary
  - Start and end times
  - Guest information
  - Creation timestamp

## Requirements

- Python 3.6+
- Google Cloud Platform project with Calendar API enabled

## Dependencies

```
google-auth
google-auth-oauthlib
google-api-python-client
pandas
```

## Setup

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up a Google Cloud Platform project:
   - Enable the Google Calendar API
   - Create OAuth 2.0 credentials
   - Download the credentials JSON file and save it as `credentials.json` in the project directory

### Domain-Wide Delegation Setup (for accessing multiple calendars)

To access calendars across your organization, you'll need domain-wide delegation set up by your Google Workspace administrator:

1. In the Google Cloud Console for your project:
   - Navigate to "APIs & Services" > "Credentials"
   - Create a service account or use an existing one
   - Download the service account JSON key file

2. In the Google Admin Console (admin.google.com):
   - Go to Security > API Controls > Domain-wide Delegation
   - Click "Add new" and enter your service account's Client ID
   - Add the following OAuth scope:
     ```
     https://www.googleapis.com/auth/calendar.readonly
     ```
   
3. This allows the application to read calendar data from all users in your domain without individual authorization

Note: This step requires administrative privileges for your Google Workspace domain. Only domain administrators can enable domain-wide delegation.

## Usage

1. First-time use will prompt for Google authentication in your browser
2. Run the script:
   ```
   python calendar_fetcher.py
   ```
3. Events from the specified calendars will be fetched and displayed
4. The script returns a pandas DataFrame that can be used for further analysis or export

## Configuration

- Modify the `calendar_ids` list to include the email addresses of calendars you want to track
- Adjust the `timeMin` parameter in the `events().list()` method to change the date range
- The script is configured to fetch events starting from January 1, 2024

### Authentication Methods

The code supports two authentication approaches:

1. **User Authentication (OAuth 2.0)**: Used by default in this script. Appropriate for personal use or when accessing a limited set of calendars with explicit user consent.

2. **Service Account with Domain-Wide Delegation**: Preferred for organizational use when accessing multiple calendars. Requires administrative setup as described in the Setup section.

If using domain-wide delegation, you'll need to modify the authentication code to use the service account credentials instead of the user OAuth flow.

## Extending the Script

This script provides a foundation that can be easily extended to:
- Export data to CSV, Excel, or other formats
- Perform analytics on meeting patterns
- Connect to databases for persistent storage
- Create visualizations of calendar usage

## Security Note

- The code uses OAuth 2.0 for secure authentication
- You'll need to securely manage your `credentials.json` file and the generated `token.pickle`
- Never share these authentication files publicly



[MIT License](LICENSE)
