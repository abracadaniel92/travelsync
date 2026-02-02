#!/usr/bin/env python3
"""
Test script to test document processing locally
Usage: python3 test_upload.py <path_to_image_or_pdf>
"""

import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.document_processor import process_document

async def test_document(file_path: str):
    """Test processing a document"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return
    
    # Determine content type
    suffix = file_path.suffix.lower()
    content_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.pdf': 'application/pdf'
    }
    
    content_type = content_types.get(suffix)
    if not content_type:
        print(f"Error: Unsupported file type: {suffix}")
        return
    
    # Read file
    print(f"Reading file: {file_path}")
    with open(file_path, 'rb') as f:
        contents = f.read()
    
    print(f"File size: {len(contents)} bytes")
    print(f"Content type: {content_type}")
    print("\nProcessing document...")
    
    try:
        travel_info = await process_document(contents, content_type)
        print("\n✅ Success! Extracted travel information:")
        print("=" * 60)
        import json
        print(json.dumps(travel_info, indent=2))
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_upload.py <path_to_image_or_pdf>")
        print("\nExample:")
        print("  python3 test_upload.py test_image.png")
        sys.exit(1)
    
    asyncio.run(test_document(sys.argv[1]))

