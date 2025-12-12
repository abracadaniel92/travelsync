"""
Google Calendar integration service
"""

import os
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import re

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Common timezone mappings for cities/airports
# This helps preserve correct times when traveling
TIMEZONE_MAP = {
    # Europe
    'skopje': 'Europe/Skopje', 'skp': 'Europe/Skopje',
    'memmingen': 'Europe/Berlin', 'munich': 'Europe/Berlin', 'münchen': 'Europe/Berlin', 'fmm': 'Europe/Berlin',
    'budapest': 'Europe/Budapest',
    'london': 'Europe/London', 'lhr': 'Europe/London', 'lgw': 'Europe/London',
    'paris': 'Europe/Paris', 'cdg': 'Europe/Paris',
    'rome': 'Europe/Rome', 'fco': 'Europe/Rome',
    'madrid': 'Europe/Madrid', 'mad': 'Europe/Madrid',
    'miami': 'America/New_York', 'mia': 'America/New_York',
    'new york': 'America/New_York', 'jfk': 'America/New_York', 'lga': 'America/New_York',
    'los angeles': 'America/Los_Angeles', 'lax': 'America/Los_Angeles',
    'tel aviv': 'Asia/Jerusalem', 'tlv': 'Asia/Jerusalem',
    'dortmund': 'Europe/Berlin',
    'cluj': 'Europe/Bucharest',
    # Add more as needed
}

def detect_timezone_from_location(location: str, title: str = "") -> Optional[str]:
    """
    Try to detect timezone from location or title.
    Returns timezone string (e.g., 'Europe/Skopje') or None if not found.
    """
    if not location:
        location = title
    
    # Combine location and title for better detection
    search_text = f"{location} {title}".lower()
    
    # Look for airport codes (3 letters)
    airport_code_match = re.search(r'\b([A-Z]{3})\b', search_text.upper())
    if airport_code_match:
        code = airport_code_match.group(1).lower()
        if code in TIMEZONE_MAP:
            return TIMEZONE_MAP[code]
    
    # Look for city names
    for city, tz in TIMEZONE_MAP.items():
        if city in search_text:
            return tz
    
    return None

def _get_project_root():
    """Get the project root directory (DocumentsToCalendar folder)"""
    # This file is in backend/services/, so go up 2 levels
    current_file = Path(__file__)
    return current_file.parent.parent.parent

async def get_calendar_service():
    """Get authenticated Google Calendar service"""
    creds = None
    project_root = _get_project_root()
    
    # Default paths relative to project root
    default_token_path = project_root / "token.pickle"
    default_credentials_path = project_root / "credentials.json"
    
    # Get paths from environment or use defaults
    token_path_str = os.getenv("GOOGLE_CALENDAR_TOKEN_PATH")
    credentials_path_str = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH")
    
    # Convert to Path objects, resolving relative paths from project root
    if token_path_str:
        token_path = Path(token_path_str)
        if not token_path.is_absolute():
            token_path = project_root / token_path
    else:
        token_path = default_token_path
    
    if credentials_path_str:
        credentials_path = Path(credentials_path_str)
        if not credentials_path.is_absolute():
            credentials_path = project_root / credentials_path
    else:
        credentials_path = default_credentials_path
    
    # Support reading credentials from environment variable (for GitHub secrets/Docker)
    # Support both naming conventions (GOOGLE_CALENDAR_CREDENTIALS_JSON or CREDENTIALS_JSON)
    credentials_json = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_JSON") or os.getenv("CREDENTIALS_JSON")
    if credentials_json:
        # Decode base64 if needed, or use JSON directly
        import json
        import base64
        try:
            # Try to decode as base64 first (common for secrets)
            decoded = base64.b64decode(credentials_json).decode('utf-8')
            credentials_data = json.loads(decoded)
        except:
            # If not base64, try parsing as JSON directly
            try:
                credentials_data = json.loads(credentials_json)
            except:
                raise ValueError("Invalid GOOGLE_CALENDAR_CREDENTIALS_JSON format")
        
        # Write to a temporary file for OAuth flow
        import tempfile
        temp_credentials = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(credentials_data, temp_credentials)
        temp_credentials.close()
        credentials_path = Path(temp_credentials.name)
    
    # Load existing token
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"Google Calendar credentials not found at {credentials_path}. "
                    f"Please download credentials.json from Google Cloud Console and place it in: {project_root}"
                )
            # Check if running in headless mode (Docker/server without display)
            headless = os.getenv("GOOGLE_CALENDAR_HEADLESS", "false").lower() == "true"
            
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            
            # In Docker/headless environments, we can't use interactive flows
            # Raise an error with instructions to use the API endpoint
            raise ValueError(
                "Google Calendar authentication required. "
                "Please visit /api/calendar/auth/start to begin authentication, "
                "or authenticate manually and copy token.pickle to the server."
            )
        
        # Save credentials for next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('calendar', 'v3', credentials=creds)
    return service

async def add_event_to_calendar(travel_info: Dict) -> Optional[str]:
    """
    Add a travel event to Google Calendar
    
    Args:
        travel_info: Dictionary with travel information from document processor
        
    Returns:
        Event ID if successful, None otherwise
    """
    try:
        service = await get_calendar_service()
        
        # Try to detect timezone from location (departure/destination)
        # This ensures times are stored in the ticket's local timezone, not your current timezone
        location = travel_info.get("location", "")
        title = travel_info.get("title", "")
        detected_timezone = detect_timezone_from_location(location, title)
        
        # Get calendar's timezone as fallback
        calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        try:
            calendar = service.calendars().get(calendarId=calendar_id).execute()
            calendar_timezone = calendar.get('timeZone', 'UTC')
        except:
            calendar_timezone = 'UTC'
        
        # Use detected timezone if found, otherwise use calendar's timezone
        event_timezone = detected_timezone or calendar_timezone
        if detected_timezone:
            print(f"Detected timezone {detected_timezone} from location: {location}")
        else:
            print(f"Using calendar timezone {calendar_timezone} (could not detect from location: {location})")
        
        # Parse dates - keep as naive datetime (no timezone) to preserve exact times from document
        start_date_str = travel_info.get("start_date", "")
        # Remove timezone if present to keep as naive datetime
        if start_date_str.endswith("Z"):
            start_date_str = start_date_str[:-1]
        elif "+" in start_date_str:
            # Has timezone offset like +00:00 or +01:00, remove it
            start_date_str = start_date_str.split("+")[0]
        start_date = datetime.fromisoformat(start_date_str)
        
        end_date = travel_info.get("end_date")
        if end_date:
            end_date_str = end_date
            # Remove timezone if present
            if end_date_str.endswith("Z"):
                end_date_str = end_date_str[:-1]
            elif "+" in end_date_str:
                end_date_str = end_date_str.split("+")[0]
            end_date = datetime.fromisoformat(end_date_str)
        else:
            # Default to 1 hour after start if no end date
            from datetime import timedelta
            end_date = start_date + timedelta(hours=1)
        
        # Create event - use detected timezone (from location) or calendar's timezone
        # This preserves the exact times from the document in the correct timezone
        event = {
            'summary': travel_info.get("title", "Travel Event"),
            'location': travel_info.get("location", ""),
            'description': travel_info.get("description", ""),
            'start': {
                'dateTime': start_date.isoformat(),
                'timeZone': event_timezone,  # Use location's timezone if detected, otherwise calendar's
            },
            'end': {
                'dateTime': end_date.isoformat(),
                'timeZone': event_timezone,  # Use location's timezone if detected, otherwise calendar's
            },
        }
        
        # Insert event
        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        
        return event_result.get('id')
        
    except Exception as e:
        print(f"Error adding event to calendar: {str(e)}")
        # Don't raise - allow the document processing to succeed even if calendar fails
        return None

