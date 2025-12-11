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

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

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
            
            if headless:
                # For headless servers, use a different flow
                # User needs to authenticate once and provide token
                raise ValueError(
                    "Headless mode: Please authenticate locally first and copy token.pickle to server. "
                    "Or set GOOGLE_CALENDAR_HEADLESS=false and ensure server has display access."
                )
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)
        
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
        
        # Parse dates
        start_date = datetime.fromisoformat(travel_info.get("start_date", "").replace("Z", "+00:00"))
        end_date = travel_info.get("end_date")
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        else:
            # Default to 1 hour after start if no end date
            from datetime import timedelta
            end_date = start_date + timedelta(hours=1)
        
        # Create event
        event = {
            'summary': travel_info.get("title", "Travel Event"),
            'location': travel_info.get("location", ""),
            'description': travel_info.get("description", ""),
            'start': {
                'dateTime': start_date.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_date.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        # Get calendar ID from environment or use primary
        calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        
        # Insert event
        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        
        return event_result.get('id')
        
    except Exception as e:
        print(f"Error adding event to calendar: {str(e)}")
        # Don't raise - allow the document processing to succeed even if calendar fails
        return None

