import pytest
from unittest.mock import patch, MagicMock
from main import run_scraper

@patch('main.update_drive_file')
@patch('main.scrape_documentation')
@patch('main.load_config')
def test_main_success(mock_load_config, mock_scrape, mock_gdocs_update):
    # Setup mocks
    mock_load_config.return_value = {
        "documentacoes": [
            {
                "nome": "Test Doc",
                "url_base": "https://test.com",
                "drive_folder_id": "12345"
            }
        ]
    }
    mock_scrape.return_value = "# Extracted Content"
    mock_gdocs_update.return_value = {"id": "12345"}
    
    # Run
    run_scraper("mock_config.json")
    
    # Verify
    mock_load_config.assert_called_once_with("mock_config.json")
    mock_scrape.assert_called_once_with("https://test.com")
    mock_gdocs_update.assert_called_once_with("12345", "Test Doc", "# Extracted Content")
    
@patch('main.update_drive_file')
@patch('main.scrape_documentation')
@patch('main.load_config')
def test_main_scrape_failure(mock_load_config, mock_scrape, mock_gdocs_update):
    mock_load_config.return_value = {
        "documentacoes": [
            {"nome": "Test Doc", "url_base": "https://test.com", "drive_folder_id": "12345"}
        ]
    }
    mock_scrape.return_value = "" # No content extracted
    
    run_scraper("mock_config.json")
    
    # gdocs should not be updated if scraping failed/returned nothing
    mock_gdocs_update.assert_not_called()

@patch('main.update_drive_file')
@patch('main.scrape_documentation')
@patch('main.load_config')
def test_main_continue_on_error(mock_load_config, mock_scrape, mock_gdocs_update):
    mock_load_config.return_value = {
        "documentacoes": [
            {"nome": "Fail Doc", "url_base": "https://fail.com", "drive_folder_id": "12345"},
            {"nome": "Success Doc", "url_base": "https://success.com", "drive_folder_id": "67890"}
        ]
    }
    
    # Mock scrape to fail on first, succeed on second
    def scrape_side_effect(url):
        if "fail" in url:
            raise Exception("Scraping failed")
        return "# Success"
        
    mock_scrape.side_effect = scrape_side_effect
    
    # Run
    run_scraper("mock_config.json")
    
    # Verify second doc was still processed
    assert mock_scrape.call_count == 2
    mock_gdocs_update.assert_called_once_with("67890", "Success Doc", "# Success")
