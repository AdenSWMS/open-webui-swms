from typing import Dict
import json
import os
from typing import Dict

MAPPING_FILE = os.getenv("MAPPING_FILE_PATH")

def load_provider_mapping() -> Dict[str, str]:
    """Lädt das Mapping aus der JSON-Datei."""
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def add_provider_to_model(model_id: str) -> str:

    mapping = load_provider_mapping()
    model_lower = model_id.lower()

    for prefix, provider in mapping.items():
        if model_lower.startswith(prefix.lower()):
            return f"{provider}/{model_id}"

    return False