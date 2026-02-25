import json
import os
from typing import Dict, Any

def load_config(filepath: str) -> Dict[str, Any]:
    """
    Loads and validates the configuration from a JSON file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Config file not found: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {filepath}: {e}")

    if "documentacoes" not in data:
        raise ValueError("Missing 'documentacoes' key in configuration")

    for doc in data["documentacoes"]:
        if not all(k in doc for k in ("nome", "url_base", "drive_file_id")):
            raise ValueError(f"Invalid document schema in {filepath}. Missing required keys.")

    return data
