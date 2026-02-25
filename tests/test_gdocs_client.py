import pytest
from unittest.mock import MagicMock, patch
from src.gdocs_client import update_google_doc

@patch('src.gdocs_client.service_account.Credentials.from_service_account_info')
@patch('src.gdocs_client.build')
@patch('src.gdocs_client.os.getenv')
def test_update_google_doc_success(mock_getenv, mock_build, mock_credentials):
    # Setup mocks
    mock_getenv.return_value = '{"project_id": "test"}'
    
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    mock_docs = MagicMock()
    mock_service.documents().get.return_value.execute.return_value = {
        'body': {
            'content': [
                {'endIndex': 1},
                {'endIndex': 50}
            ]
        }
    }
    
    # Test
    update_google_doc("12345", "# Updated Content")
    
    # Verify environment variable was read
    mock_getenv.assert_called_with('GOOGLE_CREDENTIALS_JSON')
    
    # Verify service account was initialized
    mock_credentials.assert_called_once()
    
    # Verify API calls
    mock_service.documents().get.assert_called_with(documentId="12345")
    
    # The batchUpdate should have an empty delete request and insert text request
    mock_service.documents().batchUpdate.assert_called_once()
    
    calls = mock_service.documents().batchUpdate.call_args[1]
    requests = calls['body']['requests']
    
    assert len(requests) == 2
    assert 'deleteContentRange' in requests[0]
    assert 'insertText' in requests[1]
    assert requests[1]['insertText']['text'] == "# Updated Content"

@patch('src.gdocs_client.os.getenv')
def test_update_google_doc_missing_credentials(mock_getenv):
    mock_getenv.return_value = None
    
    with pytest.raises(ValueError, match="GOOGLE_CREDENTIALS_JSON environment variable not set"):
        update_google_doc("12345", "Text")
