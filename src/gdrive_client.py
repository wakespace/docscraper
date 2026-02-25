import os
import json
import logging
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def update_drive_file(drive_file_id: str, markdown_content: str):
    """
    Overwrites the specified file in Google Drive with new plain text content.
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
        drive_service = build('drive', 'v3', credentials=creds)

        # Prepare payload as in-memory bytes
        media = MediaIoBaseUpload(
            io.BytesIO(markdown_content.encode('utf-8')),
            mimetype='text/plain',
            resumable=True
        )

        # Update the file by overwriting it completely
        result = drive_service.files().update(
            fileId=drive_file_id,
            media_body=media
        ).execute()
            
        logger.info(f"Successfully updated Drive file: {drive_file_id}")
        return result

    except HttpError as error:
        if error.resp.status == 404:
            logger.error(f"File not found on Google Drive: {drive_file_id}")
        else:
            logger.error(f"Google Drive API error: {error}")
        raise
    except Exception as e:
        logger.error(f"Failed to update document {drive_file_id}: {e}")
        raise
