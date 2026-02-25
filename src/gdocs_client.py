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

        # 1. Get the current document to find the total length
        doc = service.documents().get(documentId=document_id).execute()
        content = doc.get('body').get('content')
        
        # Calculate the end index (everything except the last character which cannot be deleted)
        end_index = 1
        if content:
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
            
        # 3. Insert new text at the beginning
        requests.append({
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': markdown_content
            }
        })

        result = service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests}).execute()
            
        logger.info(f"Successfully updated document: {document_id}")
        return result

    except Exception as e:
        logger.error(f"Failed to update document {document_id}: {e}")
        raise
