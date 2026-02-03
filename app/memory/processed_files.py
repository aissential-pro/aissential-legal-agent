"""
Persistent storage for processed file IDs.

Features:
- Atomic writes (prevents corruption on crash)
- Automatic backups
- Corruption recovery
- Thread-safe operations
"""

import json
import shutil
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Set, Optional

logger = logging.getLogger(__name__)

# File paths
MEMORY_DIR = Path(__file__).parent
PROCESSED_FILE = MEMORY_DIR / "processed.json"
BACKUP_FILE = MEMORY_DIR / "processed.backup.json"
TEMP_FILE = MEMORY_DIR / "processed.tmp.json"

# Thread lock for safe concurrent access
_lock = threading.Lock()

# In-memory cache
_cache: Optional[Set[str]] = None
_cache_dirty = False


def _load_from_file(filepath: Path) -> Set[str]:
    """Load data from a JSON file."""
    if not filepath.exists():
        return set()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return set(data)
        elif isinstance(data, dict):
            # Handle legacy format with additional metadata
            return set(data.get("ids", data.get("processed", [])))
        else:
            logger.warning(f"Unexpected data format in {filepath}")
            return set()

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {filepath}: {e}")
        return set()
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return set()


def _save_to_file(ids: Set[str], filepath: Path) -> bool:
    """
    Save data to a JSON file atomically.

    Uses a temp file and rename for atomic write.
    """
    try:
        # Write to temp file first
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(ids)), f, indent=2, ensure_ascii=False)
            f.flush()

        # Atomic rename
        TEMP_FILE.replace(filepath)
        return True

    except Exception as e:
        logger.error(f"Error saving to {filepath}: {e}")
        # Cleanup temp file on error
        if TEMP_FILE.exists():
            try:
                TEMP_FILE.unlink()
            except:
                pass
        return False


def _create_backup() -> bool:
    """Create a backup of the processed file."""
    if not PROCESSED_FILE.exists():
        return True

    try:
        shutil.copy2(PROCESSED_FILE, BACKUP_FILE)
        logger.debug("Created backup of processed files")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return False


def _recover_from_backup() -> Set[str]:
    """Attempt to recover from backup file."""
    if not BACKUP_FILE.exists():
        logger.warning("No backup file available for recovery")
        return set()

    logger.info("Attempting recovery from backup...")
    ids = _load_from_file(BACKUP_FILE)

    if ids:
        # Restore backup
        _save_to_file(ids, PROCESSED_FILE)
        logger.info(f"Recovered {len(ids)} processed IDs from backup")

    return ids


def get_processed_ids() -> Set[str]:
    """
    Load processed file IDs.

    Returns a copy of the set to prevent external modification.
    Uses in-memory cache for performance.
    """
    global _cache

    with _lock:
        if _cache is not None:
            return _cache.copy()

        # Load from main file
        ids = _load_from_file(PROCESSED_FILE)

        # If main file is corrupted/empty but backup exists, try recovery
        if not ids and BACKUP_FILE.exists():
            backup_ids = _load_from_file(BACKUP_FILE)
            if backup_ids:
                logger.warning("Main file empty/corrupted, recovering from backup")
                ids = backup_ids
                _save_to_file(ids, PROCESSED_FILE)

        _cache = ids
        return _cache.copy()


def mark_processed(file_id: str) -> bool:
    """
    Add file_id to the processed set and save.

    Returns True on success, False on failure.
    """
    global _cache, _cache_dirty

    if not file_id:
        return False

    with _lock:
        # Ensure cache is loaded
        if _cache is None:
            get_processed_ids()

        # Check if already processed
        if file_id in _cache:
            return True

        # Create backup before modification (every 10th addition)
        if len(_cache) % 10 == 0:
            _create_backup()

        # Add to cache
        _cache.add(file_id)

        # Save to file
        success = _save_to_file(_cache, PROCESSED_FILE)

        if success:
            logger.debug(f"Marked as processed: {file_id[:20]}...")
        else:
            # Rollback cache on failure
            _cache.discard(file_id)
            logger.error(f"Failed to mark as processed: {file_id}")

        return success


def is_processed(file_id: str) -> bool:
    """Check if a file ID has been processed."""
    return file_id in get_processed_ids()


def remove_processed(file_id: str) -> bool:
    """
    Remove a file ID from processed set (for reprocessing).

    Returns True on success.
    """
    global _cache

    with _lock:
        if _cache is None:
            get_processed_ids()

        if file_id not in _cache:
            return True

        _cache.discard(file_id)
        success = _save_to_file(_cache, PROCESSED_FILE)

        if not success:
            _cache.add(file_id)  # Rollback

        return success


def clear_processed() -> bool:
    """
    Reset all processed files (useful for reprocessing).

    Creates a backup before clearing.
    """
    global _cache

    with _lock:
        # Create backup first
        _create_backup()

        _cache = set()
        success = _save_to_file(_cache, PROCESSED_FILE)

        if success:
            logger.info("Cleared all processed files")
        else:
            # Try to recover from backup
            _cache = _load_from_file(BACKUP_FILE)
            logger.error("Failed to clear processed files")

        return success


def get_stats() -> dict:
    """Get statistics about processed files."""
    ids = get_processed_ids()

    return {
        "count": len(ids),
        "main_file_exists": PROCESSED_FILE.exists(),
        "backup_exists": BACKUP_FILE.exists(),
        "main_file_size": PROCESSED_FILE.stat().st_size if PROCESSED_FILE.exists() else 0,
    }


def force_backup() -> bool:
    """Force create a backup immediately."""
    with _lock:
        return _create_backup()


def invalidate_cache():
    """Invalidate the in-memory cache (useful after external modifications)."""
    global _cache
    with _lock:
        _cache = None
