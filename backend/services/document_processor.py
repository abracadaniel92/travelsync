"""
Document processing service using Google Gemini AI
"""

import google.generativeai as genai
from PIL import Image
import io
import os
import base64
from typing import Optional, Dict

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Cache the working model to avoid re-discovery (saves API calls)
_cached_model = None
_cached_model_name = None

async def process_document(file_contents: bytes, content_type: str) -> Optional[Dict]:
    """
    Process a document (image or PDF) to extract travel information
    
    Returns a dictionary with travel information:
    {
        "title": "Flight to Paris",
        "start_date": "2024-01-15T10:00:00",
        "end_date": "2024-01-15T14:00:00",
        "location": "Paris, France",
        "description": "Flight details..."
    }
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not set")
    
    try:
        # Use cached model if available (saves API calls)
        global _cached_model, _cached_model_name
        model = _cached_model
        model_name = _cached_model_name
        
        # If no cached model, try to find one (but skip test calls to save API quota)
        if model is None:
            # Try models in order of preference without testing first
            # This reduces API calls from 10+ to just 1-3 per document
            preferred_models = [
                'gemini-1.5-flash-latest',  # Fastest, cheapest
                'gemini-1.5-flash',
                'gemini-1.5-pro-latest',
                'gemini-1.5-pro',
                'gemini-2.5-flash',  # Newer model
                'gemini-pro-vision',
                'gemini-pro'
            ]
            
            # Try each model by attempting actual processing (no test calls)
            # We'll catch errors during actual processing
            model = None
            model_name = None
        
        print(f"Using Gemini model: {model_name or 'will be determined during processing'}")
        
        # Prepare image for processing
        if content_type.startswith("image/"):
            # Open image and convert to RGB format (required for Gemini)
            # This handles WEBP, PNG, JPEG, etc. and converts to a compatible format
            try:
                image = Image.open(io.BytesIO(file_contents))
            except Exception as e:
                raise ValueError(f"Failed to open image file: {str(e)}")
            
            # Convert to RGB if necessary (WEBP, RGBA, etc. need conversion)
            # Gemini requires RGB format
            if image.mode not in ('RGB', 'L'):
                # Convert RGBA, P, etc. to RGB
                if image.mode == 'RGBA':
                    # Create white background for transparent images
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
                    image = rgb_image
                elif image.mode == 'P':  # Palette mode
                    image = image.convert('RGB')
                else:
                    image = image.convert('RGB')
            elif image.mode == 'L':  # Grayscale - convert to RGB
                image = image.convert('RGB')
            
            # Ensure image is loaded into memory
            image.load()
            
            print(f"Processed image: original_format={content_type}, mode={image.mode}, size={image.size}")
        elif content_type == "application/pdf":
            # For PDFs, try to extract text first (more accurate than OCR)
            # If text extraction fails or returns little text, fall back to image conversion
            try:
                import fitz  # PyMuPDF
            except ImportError:
                raise ValueError(
                    "PDF processing requires PyMuPDF. "
                    "Install with: pip install pymupdf"
                )
            
            try:
                # Open PDF from bytes stream
                pdf_stream = io.BytesIO(file_contents)
                pdf_document = None
                try:
                    pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
                except Exception as e:
                    raise ValueError(f"Failed to open PDF file: {str(e)}")
                
                if len(pdf_document) == 0:
                    pdf_document.close()
                    raise ValueError("PDF file is empty or corrupted")
                
                # Try to extract text from first page (if PDF has selectable text)
                page = pdf_document[0]
                pdf_text = page.get_text()
                
                # If we got substantial text (more than 50 chars), use text-based processing
                if pdf_text and len(pdf_text.strip()) > 50:
                    print(f"Extracted {len(pdf_text)} characters of text from PDF")
                    # Close PDF before processing
                    pdf_document.close()
                    pdf_stream.close()
                    
                    # Process text directly with Gemini (more accurate than OCR)
                    # We'll pass the text as part of the prompt
                    text_prompt = f"""Extract travel information from this travel document text:

{pdf_text}

IMPORTANT: If this document is NOT in English, first translate all text to English, then extract the information. Work with the English translation.

Extract the information in this exact JSON format:
{{
    "title": "[Type] from [full departure location] to [full destination location]",
    "start_date": "ISO 8601 datetime with EXACT travel date and time (YYYY-MM-DDTHH:MM:SS). Use TRAVEL date, NOT invoice date. Use EXACT time as shown - do NOT add or subtract hours for timezone.",
    "end_date": "ISO 8601 datetime with EXACT arrival date and time or null. Use EXACT time as shown - do NOT add or subtract hours for timezone.",
    "location": "Destination/arrival location with FULL details as written (e.g., 'München Hbf, Seidlstraße 3a' or 'Memmingen Airport, Terminal 1')",
    "description": "COMPREHENSIVE details: Type (Flight/Bus/Train/Hotel), Ticket Number: [if visible], Booking/Order Number: [if visible], Trip ID: [if visible], Company: [full company name], From: [full departure location with details], To: [full destination location with address], Passenger: [name(s) with email/phone if available], Passengers: [count if multiple], Price: [if visible], Invoice Date: [if visible], Important Notes: [all notes, instructions, special conditions]"
}}

CRITICAL EXTRACTION RULES:
- If the document is NOT in English, translate all text to English first, then extract information from the English translation
- All extracted information must be in English (translate location names, company names, notes, etc. to English)
- Use TRAVEL DATE for start_date, NOT invoice date
- Extract times EXACTLY as shown (e.g., "11:00" = 11:00:00, NOT 12:00:00)
- Include FULL location details (addresses, terminal info, etc.)
- Include ALL ticket numbers, booking references, order numbers, trip IDs
- Include passenger contact information (email, phone) if visible
- Include number of passengers if multiple
- Include price information if visible
- Include ALL important notes, instructions, and special conditions (translated to English)
- Extract company/provider names completely (translate to English if needed)

CRITICAL TIME HANDLING:
- Extract times EXACTLY as shown in the document
- If document shows "Departure: 11:00", return "11:00:00" (NOT "12:00:00")
- If document shows "Arrival: 12:20", return "12:20:00" (NOT "13:20:00")
- Do NOT apply timezone conversions
- Do NOT add or subtract hours
- Use the time exactly as written (local time from the document)

Read the text carefully. Look for:
- "Name" or passenger field → extract name with contact info if available
- "Flight number" or ticket number → extract exactly
- "DEP / DEST" or route → extract FULL departure and destination with addresses
- Travel date → extract with correct year (e.g., "14 / Dec / 2025" = 2025-12-14)
- "Departure" or "Abfahrt" time → extract EXACTLY (no timezone conversion)
- "Arrival" or "Ankunft" time → extract EXACTLY (no timezone conversion)
- Ticket number, booking reference, order number, trip ID
- Invoice date and number (but use TRAVEL date for start_date)
- Number of passengers
- Price information
- Company/provider name
- Important notes and instructions

Return ONLY valid JSON, no other text."""
                    
                    # Use text-only model for text processing
                    # Try models in order until one works
                    text_models = [
                        'gemini-1.5-flash',
                        'gemini-1.5-pro',
                        'gemini-2.0-flash-exp',
                        'gemini-pro'
                    ]
                    
                    response = None
                    for model_name in text_models:
                        try:
                            text_model = genai.GenerativeModel(model_name)
                            response = text_model.generate_content(text_prompt)
                            print(f"Successfully used text model: {model_name}")
                            break
                        except Exception as e:
                            print(f"Text model {model_name} failed: {str(e)}")
                            continue
                    
                    if response is None:
                        raise ValueError("Could not find a working text model for PDF text extraction")
                    
                    # Parse response (same as image processing)
                    response_text = response.text.strip()
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                    import json
                    travel_info = json.loads(response_text)
                    return travel_info
                
                # Fall back to image conversion if text extraction didn't work well
                print("PDF text extraction had insufficient text, converting to image...")
                
                # Render page to image (pixmap)
                # Use higher DPI for better text quality (3x zoom for sharper text)
                mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better text quality
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Get page count before closing
                page_count = len(pdf_document)
                
                # Convert pixmap to bytes immediately (before closing document)
                img_data = pix.tobytes("png")
                
                # Clean up
                pix = None
                pdf_document.close()
                pdf_document = None
                pdf_stream.close()
                
                # Create PIL Image from the bytes
                try:
                    image = Image.open(io.BytesIO(img_data))
                except Exception as e:
                    raise ValueError(f"Failed to open PDF-converted image: {str(e)}")
                
                # Convert to RGB if necessary
                if image.mode not in ('RGB', 'L'):
                    if image.mode == 'RGBA':
                        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                        rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
                        image = rgb_image
                    elif image.mode == 'P':
                        image = image.convert('RGB')
                    else:
                        image = image.convert('RGB')
                elif image.mode == 'L':
                    image = image.convert('RGB')
                
                image.load()
                print(f"Converted PDF page 1 of {page_count} to image: mode={image.mode}, size={image.size}")
            except ValueError as e:
                # Re-raise ValueError as-is
                raise
            except Exception as e:
                error_msg = str(e)
                # Clean up if document is still open
                if 'pdf_document' in locals() and pdf_document is not None:
                    try:
                        pdf_document.close()
                    except:
                        pass
                raise ValueError(f"Error converting PDF to image: {error_msg}")
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        # Create prompt for travel document extraction
        prompt = """Extract travel information from this document. It could be a flight ticket, bus ticket, train ticket, hotel reservation, or other travel document.

IMPORTANT: If this document is NOT in English, first translate all visible text to English in your mind, then extract the information from the English translation. All extracted information should be in English.

Read the document carefully and extract ALL available information. Look for:

FOR FLIGHTS:
- "Name" or passenger name field → extract exactly as written
- "Flight number" → extract exactly (e.g., "W6 4727")
- "DEP / DEST" or route → extract departure and destination airports/cities with full details
- "Flight date" or travel date → extract with correct year
- "Departure" time → extract exactly
- "Arrival" time → extract exactly
- Airline name, gate, seat, terminal if visible
- Ticket number, booking reference, PNR if visible
- Passenger contact info (email, phone) if visible
- Number of passengers if visible
- Price information if visible
- Important notes or instructions

FOR BUS/TRAIN TICKETS:
- Passenger name(s) → extract exactly
- Departure location → extract FULL details (e.g., "Allgäu Airport Memmingen, Direct in front of Terminal 1")
- Arrival location → extract FULL details including address (e.g., "München Hbf, Seidlstraße 3a")
- Travel date → extract with correct year (NOT invoice date)
- Departure time → extract exactly (e.g., "11:00" = 11:00:00)
- Arrival time → extract exactly (e.g., "12:20" = 12:20:00)
- Ticket number, booking reference, order number, trip ID if visible
- Invoice number and date if visible (but use TRAVEL date for start_date)
- Number of passengers if visible
- Price information if visible
- Company/provider name (e.g., "Allgäu Airport Express GmbH")
- Passenger contact info (email, phone) if visible
- Important notes, instructions, or special conditions

FOR HOTELS:
- Hotel name → extract exactly
- Check-in date → extract with correct year
- Check-out date → extract with correct year
- Location/address → extract exactly
- Guest name(s) if visible
- Booking reference, confirmation number if visible
- Price information if visible

Return the information in this exact JSON format:
{
    "title": "[Type] from [departure/origin] to [destination] (e.g., 'Bus from Allgäu Airport Memmingen to München Hbf' or 'Flight from Paris to London')",
    "start_date": "ISO 8601 datetime with EXACT travel date and time from document (YYYY-MM-DDTHH:MM:SS). Use TRAVEL date, NOT invoice date. Use EXACT time as shown - do NOT add or subtract hours for timezone.",
    "end_date": "ISO 8601 datetime with EXACT arrival/checkout date and time from document or null if single event. Use EXACT time as shown - do NOT add or subtract hours for timezone.",
    "location": "Destination/arrival location with full details as written in document (e.g., 'München Hbf, Seidlstraße 3a' or 'Memmingen Airport')",
    "description": "COMPREHENSIVE details including: Type (Flight/Bus/Train/Hotel), Ticket/Booking Number: [if visible], Company/Provider name, Full route (From [full departure] to [full destination]), Passenger: [name(s) with contact info if available], Passengers: [count if multiple], Price: [if visible], Trip ID/Order Number: [if visible], Invoice Date: [if visible], Important Notes: [all notes, instructions, special conditions]"
}

IMPORTANT EXTRACTION RULES:
- If the document is NOT in English, translate all visible text to English first, then extract information from the English translation
- All extracted information must be in English (translate location names, company names, notes, etc. to English)
- Use the TRAVEL DATE for start_date, NOT invoice date or booking date
- Extract times exactly as shown (e.g., "11:00" = 11:00:00, NOT 12:00:00)
- Include FULL location details (addresses, terminal info, etc.) - translate to English if needed
- Include ALL ticket numbers, booking references, order numbers, trip IDs
- Include passenger contact information (email, phone) if visible
- Include number of passengers if multiple
- Include price information if visible
- Include ALL important notes, instructions, and special conditions (translated to English)
- Extract company/provider names completely (translate to English if needed)
- Make description comprehensive - include everything that might be useful (all in English)

CRITICAL TIME HANDLING:
- Extract times EXACTLY as shown in the document (e.g., if document shows "07:00", use "07:00:00", NOT "08:00:00")
- Do NOT apply timezone conversions
- Do NOT add or subtract hours
- Use the time exactly as written (local time from the document)
- If document shows "Departure: 07:00" and date is "14 / Dec / 2025", return "2025-12-14T07:00:00" (not 08:00:00)
- If document shows "Arrival: 09:10", return "2025-12-14T09:10:00" (not 10:10:00)

If you cannot find specific information, use null for that field. Always return valid JSON only."""

        # Process with Gemini
        # For vision models, pass image and prompt together
        # If no cached model, try models until one works
        response = None
        last_error = None
        
        if model is None:
            # Try each model in order until one works
            # Flash models first (fastest, cheapest, and worked great locally)
            # Note: Some model names may have changed, so we try multiple variants
            preferred_models = [
                'gemini-1.5-flash',  # Try without -latest suffix first
                'gemini-1.5-flash-latest',
                'gemini-1.5-pro',
                'gemini-1.5-pro-latest',
                'gemini-2.0-flash-exp',
                'gemini-2.5-flash',
                'gemini-pro-vision',
                'gemini-pro'
            ]
            
            for model_name_attempt in preferred_models:
                try:
                    test_model = genai.GenerativeModel(model_name_attempt)
                    # Ensure image is in RGB format (required by Gemini)
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Pass the PIL Image directly to Gemini - no pixel manipulation to preserve quality
                    # Gemini accepts PIL.Image.Image objects directly
                    response = test_model.generate_content([image, prompt])
                    # Success! Cache this model for future use
                    _cached_model = test_model
                    _cached_model_name = model_name_attempt
                    model_name = model_name_attempt
                    print(f"Successfully using model: {model_name_attempt}")
                    break
                except Exception as e:
                    last_error = e
                    error_msg = str(e)
                    error_type = type(e).__name__
                    print(f"Model {model_name_attempt} failed: {error_type}: {error_msg}")
                    print(f"Error details: {repr(e)}")
                    # If error mentions format issues, try with base64 encoding as last resort
                    if 'format' in error_msg.lower() or 'blob' in error_msg.lower() or 'webp' in error_msg.lower() or 'image' in error_msg.lower() or error_msg == 'WEBP':
                        try:
                            # Try converting to base64 and using that
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            # Create fresh image from pixels
                            pixels = list(image.getdata())
                            width, height = image.size
                            new_img = Image.new('RGB', (width, height))
                            new_img.putdata(pixels)
                            # Convert to base64 string
                            img_bytes = io.BytesIO()
                            new_img.save(img_bytes, format='PNG')
                            img_bytes.seek(0)
                            img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
                            # Try with base64 data URI
                            data_uri = f"data:image/png;base64,{img_base64}"
                            response = test_model.generate_content([data_uri, prompt])
                            _cached_model = test_model
                            _cached_model_name = model_name_attempt
                            model_name = model_name_attempt
                            print(f"Successfully using model {model_name_attempt} with base64")
                            break
                        except Exception as retry_error:
                            print(f"Retry also failed: {str(retry_error)}")
                            continue
                    continue
            
            if response is None:
                raise ValueError(f"Could not find any working Gemini model. Last error: {str(last_error)}")
        else:
            # Use cached model
            try:
                # Ensure image is in RGB format (required by Gemini)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Pass the PIL Image directly to Gemini - preserve original quality
                response = model.generate_content([image, prompt])
            except Exception as e:
                # Cached model failed, clear cache and try again
                error_msg = str(e)
                print(f"Cached model failed, trying alternatives: {error_msg}")
                _cached_model = None
                _cached_model_name = None
                
                # Retry with first model in list
                try:
                    test_model = genai.GenerativeModel('gemini-1.5-flash')
                    # Ensure image is in RGB format
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Pass the PIL Image directly - preserve quality
                    response = test_model.generate_content([image, prompt])
                    _cached_model = test_model
                    _cached_model_name = 'gemini-1.5-flash-latest'
                    model_name = 'gemini-1.5-flash-latest'
                except Exception as retry_error:
                    raise ValueError(f"Error processing with Gemini: {str(retry_error)}")
        
        # Parse response
        response_text = response.text.strip()
        
        # Extract JSON from response (sometimes Gemini adds markdown formatting)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        import json
        travel_info = json.loads(response_text)
        
        return travel_info
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error processing document: {error_msg}")
        # Provide more helpful error messages
        if "404" in error_msg and "not found" in error_msg:
            raise ValueError(f"Gemini model not available. The model may have been deprecated or your API key doesn't have access. Error: {error_msg}")
        elif "API key" in error_msg or "authentication" in error_msg.lower():
            raise ValueError("Invalid or missing Google API key. Please check your GOOGLE_API_KEY environment variable.")
        else:
            raise ValueError(f"Error processing document with Gemini: {error_msg}")

