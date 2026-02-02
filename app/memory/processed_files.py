import json
from pathlib import Path

PROCESSED_FILE = Path(__file__).parent / "processed.json"


def get_processed_ids() -> set:
    """Load processed file IDs from JSON file, return empty set if not exists."""
    if not PROCESSED_FILE.exists():
        return set()

    with open(PROCESSED_FILE, "r") as f:
        data = json.load(f)

    return set(data)


def mark_processed(file_id: str) -> None:
    """Add file_id to the processed set and save to JSON."""
    processed = get_processed_ids()
    processed.add(file_id)

    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed), f, indent=2)


def clear_processed() -> None:
    """Reset the processed files (useful for reprocessing)."""
    with open(PROCESSED_FILE, "w") as f:
        json.dump([], f)
