import pytest
import io
from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
from src.gdrive_client import update_drive_file

def mock_env_vars():
    return {
        'GCP_CLIENT_ID': 'fake_client_id',
        'GCP_CLIENT_SECRET': 'fake_client_secret',
        'GCP_REFRESH_TOKEN': 'fake_refresh_token'
    }

@patch('src.gdrive_client.os.environ.get')
@patch('src.gdrive_client.Credentials')
@patch('src.gdrive_client.build')
def test_update_drive_file_creation(mock_build, mock_credentials, mock_environ_get):
    env_vars = mock_env_vars()
    mock_environ_get.side_effect = lambda k: env_vars.get(k)
    
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    mock_files = MagicMock()
    mock_service.files.return_value = mock_files
    
    # Mock list() returning empty list (file does not exist)
    mock_files.list.return_value.execute.return_value = {'files': []}
    mock_files.create.return_value.execute.return_value = {"id": "new_12345"}
    
    result = update_drive_file("folder_999", "Test Doc", "New Content")
    
    mock_files.list.assert_called_once()
    assert "name='Test Doc.txt'" in mock_files.list.call_args[1]['q']
    assert "'folder_999' in parents" in mock_files.list.call_args[1]['q']
    
    mock_files.create.assert_called_once()
    mock_files.update.assert_not_called()
    
    call_args = mock_files.create.call_args[1]
    assert call_args['body']['name'] == 'Test Doc.txt'
    assert 'folder_999' in call_args['body']['parents']
    
    assert result == {"id": "new_12345"}

@patch('src.gdrive_client.os.environ.get')
@patch('src.gdrive_client.Credentials')
@patch('src.gdrive_client.build')
def test_update_drive_file_update(mock_build, mock_credentials, mock_environ_get):
    env_vars = mock_env_vars()
    mock_environ_get.side_effect = lambda k: env_vars.get(k)
    
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    mock_files = MagicMock()
    mock_service.files.return_value = mock_files
    
    # Mock list() returning an existing file ID
    mock_files.list.return_value.execute.return_value = {'files': [{'id': 'existing_123'}]}
    mock_files.update.return_value.execute.return_value = {"id": "existing_123"}
    
    result = update_drive_file("folder_999", "Test Doc", "New Content")
    
    mock_files.list.assert_called_once()
    mock_files.create.assert_not_called()
    mock_files.update.assert_called_once()
    
    call_args = mock_files.update.call_args[1]
    assert call_args['fileId'] == 'existing_123'
    
    assert result == {"id": "existing_123"}

@patch('src.gdrive_client.os.environ.get')
def test_update_drive_file_missing_credentials(mock_environ_get):
    mock_environ_get.side_effect = lambda k: None
    
    with pytest.raises(ValueError, match="Missing OAuth2 environment variables"):
        update_drive_file("folder_999", "Test Doc", "Text")
