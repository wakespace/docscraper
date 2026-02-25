import os
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/documents']

def update_google_doc(document_id: str, markdown_content: str):
    """
    Erases the current content of the specified Google Doc and inserts the new Markdown content.
    """
    creds_json_str = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not creds_json_str:
        raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable not set")
        
    try:
        creds_info = json.loads(creds_json_str)
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=SCOPES)
    except Exception as e:
        raise ValueError(f"Failed to parse credentials: {e}")

    try:
        service = build('docs', 'v1', credentials=creds)

        # 1. Get the current document to find the exact end index
        doc = service.documents().get(documentId=document_id).execute()
        content = doc.get('body').get('content')
        
        # Calculate the end index (everything except the last newline character which cannot be deleted)
        end_index = 1
        if content:
            # The last element contains the end index of the body
            end_index = content[-1].get('endIndex') - 1
            
        requests = []
        
        # 2. Delete existing content (if there is any to delete)
        if end_index > 1:
            requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': end_index
                    }
                }
            })
            
        # 3. Insert new text in chunks to avoid payload size limits
        MAX_CHARS_PER_REQUEST = 500000 # 500k chars per chunk as a safe limit
        for i in range(0, len(markdown_content), MAX_CHARS_PER_REQUEST):
            chunk = markdown_content[i:i + MAX_CHARS_PER_REQUEST]
            requests.append({
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': chunk
                }
            })

        # Process in chunks of 50 requests max for safety or just bulk it if small
        # Given we chunk the text, there might be a few requests.
        result = service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests}).execute()
            
        logger.info(f"Successfully updated document: {document_id}")
        return result

    except Exception as e:
        logger.error(f"Failed to update document {document_id}: {e}")
        raise
