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
            image = Image.open(io.BytesIO(file_contents))
        elif content_type == "application/pdf":
            # Convert PDF to image(s) - use first page
            try:
                import fitz  # PyMuPDF
            except ImportError:
                raise ValueError(
                    "PDF processing requires PyMuPDF. "
                    "Install with: pip install pymupdf"
                )
            
            try:
                # Open PDF from bytes stream using BytesIO for better compatibility
                pdf_stream = io.BytesIO(file_contents)
                pdf_document = None
                try:
                    pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
                except Exception as e:
                    raise ValueError(f"Failed to open PDF file: {str(e)}")
                
                if len(pdf_document) == 0:
                    pdf_document.close()
                    raise ValueError("PDF file is empty or corrupted")
                
                # Get first page (most travel documents are single page)
                page = pdf_document[0]
                
                # Render page to image (pixmap)
                # Use high DPI for better quality
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Get page count before closing
                page_count = len(pdf_document)
                
                # Convert pixmap to bytes immediately (before closing document)
                # This ensures we have all the data we need
                img_data = pix.tobytes("png")
                
                # Clean up pixmap explicitly to free memory
                pix = None
                
                # Now safe to close the document
                pdf_document.close()
                pdf_document = None
                
                # Close the stream
                pdf_stream.close()
                
                # Create PIL Image from the bytes (this is independent of the PDF)
                # Load the image fully to ensure it's not dependent on the PDF
                image = Image.open(io.BytesIO(img_data))
                # Force loading the image data
                image.load()
                
                print(f"Converted PDF page 1 of {page_count} to image")
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
        prompt = """Extract travel information from this document (ticket, boarding pass, hotel reservation, etc.).

Return the information in this exact JSON format:
{
    "title": "Brief description (e.g., 'Flight to Paris' or 'Hotel Reservation')",
    "start_date": "ISO 8601 datetime (e.g., '2024-01-15T10:00:00')",
    "end_date": "ISO 8601 datetime (e.g., '2024-01-15T14:00:00') or null if single event",
    "location": "Location name (e.g., 'Paris, France' or 'Hotel Name, City')",
    "description": "Additional details from the document"
}

If you cannot find specific information, use null for that field. Always return valid JSON only."""

        # Process with Gemini
        # For vision models, pass image and prompt together
        # If no cached model, try models until one works
        response = None
        last_error = None
        
        if model is None:
            # Try each model in order until one works
            preferred_models = [
                'gemini-1.5-flash-latest',
                'gemini-1.5-flash',
                'gemini-1.5-pro-latest',
                'gemini-1.5-pro',
                'gemini-2.5-flash',
                'gemini-pro-vision',
                'gemini-pro'
            ]
            
            for model_name_attempt in preferred_models:
                try:
                    test_model = genai.GenerativeModel(model_name_attempt)
                    response = test_model.generate_content([image, prompt])
                    # Success! Cache this model for future use
                    _cached_model = test_model
                    _cached_model_name = model_name_attempt
                    model_name = model_name_attempt
                    print(f"Successfully using model: {model_name_attempt}")
                    break
                except Exception as e:
                    last_error = e
                    continue
            
            if response is None:
                raise ValueError(f"Could not find any working Gemini model. Last error: {str(last_error)}")
        else:
            # Use cached model
            try:
                response = model.generate_content([image, prompt])
            except Exception as e:
                # Cached model failed, clear cache and try again
                print(f"Cached model failed, trying alternatives: {e}")
                _cached_model = None
                _cached_model_name = None
                
                # Retry with first model in list
                try:
                    test_model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    response = test_model.generate_content([image, prompt])
                    _cached_model = test_model
                    _cached_model_name = 'gemini-1.5-flash-latest'
                    model_name = 'gemini-1.5-flash-latest'
                except:
                    raise ValueError(f"Error processing with Gemini: {str(e)}")
        
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

