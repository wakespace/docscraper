import pytest
import io
from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
from src.gdrive_client import update_drive_file

@patch('src.gdrive_client.service_account.Credentials.from_service_account_info')
@patch('src.gdrive_client.build')
@patch('src.gdrive_client.os.getenv')
def test_update_drive_file_success(mock_getenv, mock_build, mock_credentials):
    # Setup mocks
    mock_getenv.return_value = '{"project_id": "test"}'
    
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    mock_files = MagicMock()
    mock_service.files.return_value = mock_files
    mock_files.update.return_value.execute.return_value = {"id": "12345"}
    
    # Test
    result = update_drive_file("12345", "New Context Data")
    
    # Verify environment variable was read
    mock_getenv.assert_called_with('GOOGLE_CREDENTIALS_JSON')
    mock_credentials.assert_called_once()
    mock_build.assert_called_once_with('drive', 'v3', credentials=mock_credentials.return_value)
    
    # Verify API calls
    mock_service.files().update.assert_called_once()
    
    # Extract the args to verify media upload
    call_args = mock_service.files().update.call_args[1]
    assert call_args['fileId'] == "12345"
    
    media = call_args['media_body']
    # media is a MediaIoBaseUpload object
    assert media.mimetype() == 'text/plain'
    
    # Check that bytes match
    assert media._fd.getvalue() == b"New Context Data"
    
@patch('src.gdrive_client.os.getenv')
def test_update_drive_file_missing_credentials(mock_getenv):
    mock_getenv.return_value = None
    
    with pytest.raises(ValueError, match="GOOGLE_CREDENTIALS_JSON environment variable not set"):
        update_drive_file("12345", "Text")

@patch('src.gdrive_client.service_account.Credentials.from_service_account_info')
@patch('src.gdrive_client.build')
@patch('src.gdrive_client.os.getenv')
def test_update_drive_file_404_not_found(mock_getenv, mock_build, mock_credentials):
    mock_getenv.return_value = '{"project_id": "test"}'
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    # Mock HttpError for 404
    mock_resp = MagicMock()
    mock_resp.status = 404
    http_error = HttpError(resp=mock_resp, content=b'File not found')
    
    mock_service.files().update.return_value.execute.side_effect = http_error
    
    with pytest.raises(HttpError):
        update_drive_file("wrong_id", "Text")
