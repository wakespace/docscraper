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

def update_drive_file(drive_folder_id: str, nome: str, markdown_content: str):
    """
    Overwrites or creates a plain text file inside the specified Google Drive folder.
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

        file_name = f"{nome}.txt"
        
        # Step A: Search for the file in the specific folder
        query = f"name='{file_name}' and '{drive_folder_id}' in parents and trashed=false"
        response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = response.get('files', [])

        # Prepare payload as in-memory bytes
        media = MediaIoBaseUpload(
            io.BytesIO(markdown_content.encode('utf-8')),
            mimetype='text/plain',
            resumable=True
        )

        if not files:
            # Step B1: Create a new file
            file_metadata = {
                'name': file_name,
                'parents': [drive_folder_id]
            }
            result = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            logger.info(f"Created new Drive file {file_name} with ID: {result.get('id')} in folder: {drive_folder_id}")
            return result
        else:
            # Step B2: Update existing file
            existing_file_id = files[0].get('id')
            result = drive_service.files().update(
                fileId=existing_file_id,
                media_body=media
            ).execute()
            logger.info(f"Successfully updated Drive file {file_name} with ID: {existing_file_id}")
            return result

    except HttpError as error:
        logger.error(f"Google Drive API error: {error}")
        raise
    except Exception as e:
        logger.error(f"Failed to update document {nome}: {e}")
        raise
