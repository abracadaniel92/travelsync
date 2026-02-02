"""
Documents to Calendar - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
import os
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import asyncio
import logging

from backend.auth import verify_token, get_current_user, create_access_token
from backend.models import init_db, create_admin_user
from backend.services.document_processor import process_document
from backend.services.calendar_service import add_event_to_calendar
from backend.services.email_service import get_email_service

# Load environment variables
load_dotenv()

# Background task for automatic email checking
async def auto_check_emails():
    """Background task to automatically check emails periodically"""
    email_check_interval = int(os.getenv("EMAIL_CHECK_INTERVAL", "300"))  # Default: 5 minutes
    
    while True:
        try:
            await asyncio.sleep(email_check_interval)
            
            # Check if email is configured
            email_address = os.getenv("EMAIL_ADDRESS")
            email_password = os.getenv("EMAIL_PASSWORD")
            
            if email_address and email_password:
                try:
                    email_service = get_email_service()
                    emails = await email_service.check_emails(mark_as_read=True)
                    
                    if emails:
                        print(f"Auto-check found {len(emails)} email(s) with attachments")
                        
                        # Process each email
                        for email_info in emails:
                            try:
                                for filename, content, content_type in email_info["attachments"]:
                                    try:
                                        travel_info = await process_document(content, content_type)
                                        if travel_info:
                                            event_id = await add_event_to_calendar(travel_info)
                                            print(f"Auto-processed {filename}: Created event {event_id}")
                                    except Exception as e:
                                        print(f"Error processing {filename}: {e}")
                                
                                # Move email to processed/failed folder
                                if email_info.get("errors"):
                                    await email_service.move_email(email_info["email_id"], email_service.failed_folder)
                                else:
                                    await email_service.move_email(email_info["email_id"], email_service.processed_folder)
                            except Exception as e:
                                print(f"Error processing email {email_info.get('email_id')}: {e}")
                except Exception as e:
                    print(f"Error in auto email check: {e}")
        except Exception as e:
            print(f"Error in background email checker: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying on error

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Start background email checker if enabled
    auto_check_enabled = os.getenv("EMAIL_AUTO_CHECK", "false").lower() == "true"
    if auto_check_enabled:
        print("Starting automatic email checker...")
        task = asyncio.create_task(auto_check_emails())
        yield
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    else:
        yield

app = FastAPI(
    title="TravelSync API", 
    version="1.0.0",
    lifespan=lifespan
)

# Global exception handler to ensure JSON responses (but not for HTTPException)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc  # Let FastAPI handle HTTPException normally
    print(f"Unhandled exception: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize database
init_db()
# Create admin user lazily (on first request) to avoid startup issues
# create_admin_user()  # Will be called on first login attempt

# Serve frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def root():
    """Serve the main frontend page"""
    frontend_index = frontend_path / "index.html"
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    return {"message": "TravelSync API"}

@app.get("/login")
async def login_page():
    """Serve the login page"""
    login_page_path = frontend_path / "login.html"
    if login_page_path.exists():
        return FileResponse(str(login_page_path))
    return {"message": "Login page"}

@app.post("/api/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Authenticate user and return JWT token
    """
    try:
        from backend.auth import authenticate_user
        
        user = authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process a document to extract travel information
    """
    # Store content type FIRST before reading file (prevents "body is locked" error)
    content_type = file.content_type or "application/octet-stream"
    
    # Validate file type BEFORE reading
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and images are allowed."
        )
    
    # Read file contents once and store (prevents "body is locked" error)
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Validate file size (max 5MB)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    try:
        # Process document with AI (using stored contents, not file object)
        travel_info = await process_document(contents, content_type)
        
        # Add to calendar
        if travel_info:
            event_id = await add_event_to_calendar(travel_info)
            return {
                "success": True,
                "travel_info": travel_info,
                "calendar_event_id": event_id
            }
        else:
            return {
                "success": False,
                "message": "Could not extract travel information from document"
            }
    except ValueError as e:
        # ValueError from process_document (e.g., invalid API key, model not found)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error processing document: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/email/status")
async def email_status(current_user: dict = Depends(get_current_user)):
    """Check email configuration status"""
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    imap_server = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
    
    return {
        "configured": bool(email_address and email_password),
        "email_address": email_address if email_address else None,
        "imap_server": imap_server,
        "has_password": bool(email_password)
    }

@app.post("/api/email/test")
async def test_email_connection(current_user: dict = Depends(get_current_user)):
    """Test email connection without processing emails"""
    try:
        email_service = get_email_service()
        
        # Try to connect to email server
        mail = email_service._get_connection()
        
        try:
            # Test by selecting inbox
            mail.select("INBOX")
            imap_status, messages = mail.search(None, "ALL")
            
            # Count total emails (just to verify connection works)
            email_count = len(messages[0].split()) if imap_status == "OK" else 0
            
            mail.close()
            mail.logout()
            
            return {
                "success": True,
                "message": "Email connection successful!",
                "email_address": email_service.email_address,
                "imap_server": email_service.imap_server,
                "total_emails_in_inbox": email_count
            }
        except Exception as e:
            try:
                mail.close()
                mail.logout()
            except:
                pass
            raise e
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email connection failed: {str(e)}"
        )

@app.post("/api/email/webhook")
async def email_webhook(
    request: Request,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """
    Webhook endpoint to receive emails from services like SendGrid, Mailgun, etc.
    Can be called without authentication if API key is set via X-API-Key header
    """
    webhook_api_key = os.getenv("EMAIL_WEBHOOK_API_KEY")
    
    # Optional API key authentication
    if webhook_api_key and x_api_key != webhook_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    try:
        # Try to parse email from request
        content_type = request.headers.get("content-type", "")
        
        if "multipart/form-data" in content_type:
            form = await request.form()
            
            # Mailgun format
            if "attachment-count" in form:
                # Process Mailgun webhook
                sender = form.get("sender", "Unknown")
                subject = form.get("subject", "No Subject")
                
                # Get attachments
                attachments = []
                attachment_count = int(form.get("attachment-count", 0))
                
                for i in range(attachment_count):
                    attachment = form.get(f"attachment-{i+1}")
                    if attachment:
                        filename = attachment.filename
                        content = await attachment.read()
                        content_type_attr = attachment.content_type or "application/octet-stream"
                        
                        if content_type_attr.startswith("image/") or content_type_attr == "application/pdf":
                            attachments.append((filename, content, content_type_attr))
                
                results = []
                for filename, content, content_type_attr in attachments:
                    try:
                        travel_info = await process_document(content, content_type_attr)
                        if travel_info:
                            event_id = await add_event_to_calendar(travel_info)
                            results.append({
                                "filename": filename,
                                "success": True,
                                "event_id": event_id
                            })
                    except Exception as e:
                        results.append({
                            "filename": filename,
                            "success": False,
                            "error": str(e)
                        })
                
                return {
                    "success": True,
                    "message": f"Processed {len(attachments)} attachment(s) from {sender}",
                    "results": results
                }
        
            # Try to parse raw email
        try:
            body = await request.body()
            import email as email_lib
            msg = email_lib.message_from_bytes(body)
            
            from backend.services.email_service import extract_attachments_from_message
            attachments = extract_attachments_from_message(msg)
            
            if attachments:
                results = []
                for filename, content, content_type_attr in attachments:
                    try:
                        travel_info = await process_document(content, content_type_attr)
                        if travel_info:
                            event_id = await add_event_to_calendar(travel_info)
                            results.append({
                                "filename": filename,
                                "success": True,
                                "event_id": event_id
                            })
                    except Exception as e:
                        results.append({
                            "filename": filename,
                            "success": False,
                            "error": str(e)
                        })
                
                return {
                    "success": True,
                    "message": f"Processed {len(attachments)} attachment(s)",
                    "results": results
                }
        except:
            pass
        
        return {
            "success": False,
            "message": "Could not parse email from webhook"
        }
    
    except Exception as e:
        print(f"Webhook error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@app.post("/api/email/check")
async def check_emails(current_user: dict = Depends(get_current_user)):
    """
    Check for new emails with attachments and process them
    Returns list of processed emails
    """
    try:
        email_service = get_email_service()
        
        # Check for new emails
        emails = await email_service.check_emails(mark_as_read=True)
        
        if not emails:
            return {
                "success": True,
                "message": "No new emails with attachments found",
                "emails_processed": 0,
                "results": []
            }
        
        results = []
        
        for email_info in emails:
            email_result = {
                "email_id": email_info["email_id"],
                "subject": email_info["subject"],
                "sender": email_info["sender"],
                "date": email_info["date"],
                "attachments_processed": 0,
                "events_created": 0,
                "errors": []
            }
            
            # Process each attachment
            for filename, content, content_type in email_info["attachments"]:
                try:
                    # Process document
                    travel_info = await process_document(content, content_type)
                    
                    if travel_info:
                        # Add to calendar
                        event_id = await add_event_to_calendar(travel_info)
                        email_result["attachments_processed"] += 1
                        if event_id:
                            email_result["events_created"] += 1
                    else:
                        email_result["errors"].append(f"Could not extract info from {filename}")
                
                except Exception as e:
                    error_msg = f"Error processing {filename}: {str(e)}"
                    email_result["errors"].append(error_msg)
                    print(error_msg)
            
            # Move email to processed folder if successful, failed folder if errors
            try:
                if email_result["errors"]:
                    await email_service.move_email(email_info["email_id"], email_service.failed_folder)
                else:
                    await email_service.move_email(email_info["email_id"], email_service.processed_folder)
            except Exception as e:
                print(f"Error moving email: {e}")
            
            results.append(email_result)
        
        total_processed = sum(r["attachments_processed"] for r in results)
        total_events = sum(r["events_created"] for r in results)
        
        return {
            "success": True,
            "message": f"Processed {len(emails)} email(s) with {total_processed} attachment(s)",
            "emails_processed": len(emails),
            "attachments_processed": total_processed,
            "events_created": total_events,
            "results": results
        }
    
    except ValueError as e:
        # Configuration error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error checking emails: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking emails: {str(e)}"
        )

@app.get("/api/calendar/test")
async def test_calendar_connection(current_user: dict = Depends(get_current_user)):
    """Test Google Calendar connection and authentication"""
    try:
        from backend.services.calendar_service import get_calendar_service
        
        service = await get_calendar_service()
        
        # Try to get calendar list to verify connection
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        # Get primary calendar info
        primary_calendar = next((c for c in calendars if c.get('primary')), None)
        
        if primary_calendar:
            return {
                "success": True,
                "message": "Google Calendar connection successful!",
                "calendar_name": primary_calendar.get('summary', 'Primary'),
                "calendar_id": primary_calendar.get('id'),
                "timezone": primary_calendar.get('timeZone', 'Unknown'),
                "total_calendars": len(calendars)
            }
        else:
            return {
                "success": True,
                "message": "Google Calendar connected, but no primary calendar found",
                "total_calendars": len(calendars)
            }
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calendar credentials not found: {str(e)}"
        )
    except ValueError as e:
        # This is raised when authentication is needed
        error_msg = str(e)
        if "authentication required" in error_msg.lower() or "visit /api/calendar/auth/start" in error_msg.lower():
            return {
                "success": False,
                "error": "Google Calendar authentication required. Please authenticate using the button below.",
                "details": error_msg,
                "needs_auth": True
            }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        error_msg = str(e)
        # Check for various authentication-related errors
        auth_keywords = ["invalid_grant", "token", "expired", "authentication required", "authentication", "unauthorized", "credentials"]
        if any(keyword in error_msg.lower() for keyword in auth_keywords):
            return {
                "success": False,
                "error": "Google Calendar authentication required. Please authenticate using the button below.",
                "details": error_msg,
                "needs_auth": True
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calendar connection failed: {error_msg}"
        )

@app.get("/api/calendar/auth/start")
async def start_calendar_auth(current_user: dict = Depends(get_current_user)):
    """Get Google Calendar authorization URL"""
    try:
        import os
        from pathlib import Path
        from google_auth_oauthlib.flow import InstalledAppFlow
        import json
        import base64
        import tempfile
        
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        
        # Get credentials path
        project_root = Path(__file__).parent.parent
        credentials_path_str = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "/app/data/credentials.json")
        credentials_path = Path(credentials_path_str)
        
        if not credentials_path.is_absolute():
            credentials_path = project_root / credentials_path
        
        # Support reading from environment variable
        credentials_json = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_JSON") or os.getenv("CREDENTIALS_JSON")
        if credentials_json:
            try:
                decoded = base64.b64decode(credentials_json).decode('utf-8')
                credentials_data = json.loads(decoded)
            except:
                try:
                    credentials_data = json.loads(credentials_json)
                except:
                    raise ValueError("Invalid GOOGLE_CALENDAR_CREDENTIALS_JSON format")
            
            temp_credentials = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(credentials_data, temp_credentials)
            temp_credentials.close()
            credentials_path = Path(temp_credentials.name)
        
        if not credentials_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Credentials not found at {credentials_path}"
            )
        
        # Create flow and get authorization URL
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # Use out-of-band flow
        
        authorization_url, _ = flow.authorization_url(prompt='consent')
        
        return {
            "authorization_url": authorization_url,
            "instructions": "Visit the URL above, authorize the app, and copy the authorization code. Then use /api/calendar/auth/complete with the code."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start authentication: {str(e)}"
        )

@app.post("/api/calendar/auth/complete")
async def complete_calendar_auth(
    code: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Complete Google Calendar authentication with authorization code"""
    try:
        import os
        from pathlib import Path
        from google_auth_oauthlib.flow import InstalledAppFlow
        import json
        import base64
        import tempfile
        import pickle
        
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        
        # Get credentials path
        project_root = Path(__file__).parent.parent
        credentials_path_str = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "/app/data/credentials.json")
        credentials_path = Path(credentials_path_str)
        
        if not credentials_path.is_absolute():
            credentials_path = project_root / credentials_path
        
        # Support reading from environment variable
        credentials_json = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_JSON") or os.getenv("CREDENTIALS_JSON")
        if credentials_json:
            try:
                decoded = base64.b64decode(credentials_json).decode('utf-8')
                credentials_data = json.loads(decoded)
            except:
                try:
                    credentials_data = json.loads(credentials_json)
                except:
                    raise ValueError("Invalid GOOGLE_CALENDAR_CREDENTIALS_JSON format")
            
            temp_credentials = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(credentials_data, temp_credentials)
            temp_credentials.close()
            credentials_path = Path(temp_credentials.name)
        
        if not credentials_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Credentials not found at {credentials_path}"
            )
        
        # Get token path
        token_path_str = os.getenv("GOOGLE_CALENDAR_TOKEN_PATH", "/app/data/token.pickle")
        token_path = Path(token_path_str)
        if not token_path.is_absolute():
            token_path = project_root / token_path
        
        # Create flow and exchange code for token
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Save token
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'wb') as token_file:
            pickle.dump(creds, token_file)
        
        return {
            "success": True,
            "message": "Google Calendar authentication completed successfully!"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete authentication: {str(e)}"
        )

@app.get("/api/test/gemini")
async def test_gemini(current_user: dict = Depends(get_current_user)):
    """
    Test endpoint to verify Gemini API is working
    Requires authentication
    """
    try:
        import google.generativeai as genai
        from PIL import Image
        import io
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "GOOGLE_API_KEY not set in environment variables"
            }
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with a simple text prompt (no image needed for basic test)
        try:
            # First, list available models to find what works
            try:
                models = genai.list_models()
                available_models = []
                for m in models:
                    if 'generateContent' in m.supported_generation_methods:
                        # Extract just the model name (remove 'models/' prefix)
                        model_name_clean = m.name.replace('models/', '')
                        available_models.append(model_name_clean)
                
                # Try to find a working model
                model = None
                model_name = None
                
                # Prefer models with 'flash' or 'pro' in the name
                preferred_models = [m for m in available_models if 'flash' in m.lower() or 'pro' in m.lower()]
                other_models = [m for m in available_models if m not in preferred_models]
                model_list = preferred_models + other_models
                
                for model_name_attempt in model_list[:5]:  # Try first 5 available models
                    try:
                        model = genai.GenerativeModel(model_name_attempt)
                        # Test if it actually works with a simple prompt
                        test_response = model.generate_content("Hi")
                        model_name = model_name_attempt
                        break
                    except Exception as e:
                        continue
                
                if model is None:
                    return {
                        "success": False,
                        "error": f"Could not find any working Gemini model.",
                        "available_models": available_models[:10],
                        "api_key_set": True
                    }
                
                response = model.generate_content("Say 'Hello, Gemini is working!' in exactly those words.")
                
                return {
                    "success": True,
                    "message": "Gemini API is working!",
                    "response": response.text,
                    "model_used": model_name,
                    "available_models_count": len(available_models),
                    "api_key_set": True
                }
            except Exception as list_error:
                # If listing models fails, try direct model access
                for model_name_attempt in ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-pro']:
                    try:
                        model = genai.GenerativeModel(model_name_attempt)
                        response = model.generate_content("Say 'Hello, Gemini is working!' in exactly those words.")
                        return {
                            "success": True,
                            "message": "Gemini API is working!",
                            "response": response.text,
                            "model_used": model_name_attempt,
                            "api_key_set": True
                        }
                    except:
                        continue
                
                return {
                    "success": False,
                    "error": f"Could not access Gemini models. List models error: {str(list_error)}",
                    "api_key_set": True
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Gemini API error: {str(e)}",
                "api_key_set": True
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Test failed: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

