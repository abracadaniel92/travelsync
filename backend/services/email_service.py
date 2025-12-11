"""
Email service for receiving and processing travel documents via email
"""

import imaplib
import email
from email.header import decode_header
import os
from typing import List, Dict, Optional, Tuple
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Make _extract_attachments accessible for webhook
def extract_attachments_from_message(msg):
    """Extract attachments from email message (public wrapper)"""
    service = EmailService()
    return service._extract_attachments(msg)

class EmailService:
    """Service for receiving and processing emails"""
    
    def __init__(self):
        self.imap_server = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
        self.imap_port = int(os.getenv("EMAIL_IMAP_PORT", "993"))
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")  # App password for Gmail
        self.processed_folder = os.getenv("EMAIL_PROCESSED_FOLDER", "Processed")
        self.failed_folder = os.getenv("EMAIL_FAILED_FOLDER", "Failed")
        
    def _decode_mime_words(self, s):
        """Decode MIME encoded words in email headers"""
        decoded_fragments = decode_header(s)
        decoded_str = ""
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                decoded_str += fragment.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_str += fragment
        return decoded_str
    
    def _get_connection(self) -> imaplib.IMAP4_SSL:
        """Create and return IMAP connection"""
        if not self.email_address or not self.email_password:
            raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set")
        
        mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        mail.login(self.email_address, self.email_password)
        return mail
    
    def _extract_attachments(self, msg: email.message.Message) -> List[Tuple[str, bytes, str]]:
        """Extract attachments from email message
        
        Returns list of tuples: (filename, content, content_type)
        """
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Check if part is an attachment
                if "attachment" in content_disposition or "inline" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_mime_words(filename)
                        payload = part.get_payload(decode=True)
                        content_type = part.get_content_type()
                        
                        # Only process images and PDFs
                        if content_type.startswith("image/") or content_type == "application/pdf":
                            attachments.append((filename, payload, content_type))
        else:
            # Single part message - check if it's an attachment
            filename = msg.get_filename()
            if filename:
                filename = self._decode_mime_words(filename)
                payload = msg.get_payload(decode=True)
                content_type = msg.get_content_type()
                
                if content_type.startswith("image/") or content_type == "application/pdf":
                    attachments.append((filename, payload, content_type))
        
        return attachments
    
    async def check_emails(self, mark_as_read: bool = True) -> List[Dict]:
        """Check for new emails and return unread messages with attachments
        
        Returns list of email info dicts with:
        - email_id: IMAP message ID
        - subject: Email subject
        - sender: Email sender
        - date: Email date
        - attachments: List of (filename, content, content_type) tuples
        """
        try:
            # Run IMAP operations in thread pool since imaplib is blocking
            loop = asyncio.get_event_loop()
            emails = await loop.run_in_executor(None, self._check_emails_sync, mark_as_read)
            return emails
        except Exception as e:
            logger.error(f"Error checking emails: {e}")
            raise
    
    def _check_emails_sync(self, mark_as_read: bool) -> List[Dict]:
        """Synchronous email checking (runs in thread pool)"""
        mail = self._get_connection()
        emails_found = []
        
        try:
            # Select inbox
            mail.select("INBOX")
            
            # Search for unread emails
            status, messages = mail.search(None, "UNSEEN")
            
            if status != "OK":
                logger.warning("Failed to search emails")
                return emails_found
            
            email_ids = messages[0].split()
            
            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = mail.fetch(email_id, "(RFC822)")
                    
                    if status != "OK":
                        continue
                    
                    # Parse email
                    email_body = msg_data[0][1]
                    msg = email.message_from_bytes(email_body)
                    
                    # Extract email info
                    subject = self._decode_mime_words(msg["Subject"] or "No Subject")
                    sender = self._decode_mime_words(msg["From"] or "Unknown")
                    date_str = msg["Date"] or ""
                    
                    # Extract attachments
                    attachments = self._extract_attachments(msg)
                    
                    if attachments:
                        emails_found.append({
                            "email_id": email_id.decode(),
                            "subject": subject,
                            "sender": sender,
                            "date": date_str,
                            "attachments": attachments
                        })
                        
                        # Mark as read if requested
                        if mark_as_read:
                            mail.store(email_id, "+FLAGS", "\\Seen")
                
                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}")
                    continue
        
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass
        
        return emails_found
    
    async def move_email(self, email_id: str, folder: str):
        """Move email to specified folder"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._move_email_sync, email_id, folder)
        except Exception as e:
            logger.error(f"Error moving email {email_id} to {folder}: {e}")
            raise
    
    def _move_email_sync(self, email_id: str, folder: str):
        """Synchronously move email to folder"""
        mail = self._get_connection()
        try:
            # Create folder if it doesn't exist
            try:
                mail.create(folder)
            except:
                pass  # Folder might already exist
            
            # Copy email to folder
            mail.select("INBOX")
            mail.copy(email_id, folder)
            
            # Delete from inbox
            mail.store(email_id, "+FLAGS", "\\Deleted")
            mail.expunge()
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass

# Global email service instance
_email_service: Optional[EmailService] = None

def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

