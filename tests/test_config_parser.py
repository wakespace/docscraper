import pytest
import json
import os
from src.config_parser import load_config

def test_load_config_success(tmp_path):
    # Create a temporary valid config file
    config_data = {
        "documentacoes": [
            {
                "nome": "Test Doc",
                "url_base": "https://test.com",
                "drive_file_id": "12345"
            }
        ]
    }
    config_file = tmp_path / "docs_links.json"
    config_file.write_text(json.dumps(config_data))

    # Test
    loaded_config = load_config(str(config_file))
    assert loaded_config == config_data

def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_config("non_existent_file.json")

def test_load_config_invalid_json(tmp_path):
    # Create a temporary invalid JSON file
    config_file = tmp_path / "docs_links.json"
    config_file.write_text("{invalid json")

    with pytest.raises(ValueError, match="Invalid JSON format"):
        load_config(str(config_file))

def test_load_config_missing_documentacoes(tmp_path):
    config_data = {"other_key": []}
    config_file = tmp_path / "docs_links.json"
    config_file.write_text(json.dumps(config_data))

    with pytest.raises(ValueError, match="Missing 'documentacoes' key"):
        load_config(str(config_file))

def test_load_config_invalid_document_schema(tmp_path):
    config_data = {
        "documentacoes": [
            {"nome": "Test Doc"} # Missing url_base and drive_file_id
        ]
    }
    config_file = tmp_path / "docs_links.json"
    config_file.write_text(json.dumps(config_data))

    with pytest.raises(ValueError, match="Invalid document schema"):
        load_config(str(config_file))
