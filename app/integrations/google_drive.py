import logging
from io import BytesIO

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from config.settings import (
    GOOGLE_DRIVE_FOLDER_IDS,
    GOOGLE_APPLICATION_CREDENTIALS,
    BASE_DIR,
)
from services.contract_analyzer import analyze_contract
from services import file_parser
from memory.processed_files import get_processed_ids, mark_processed
from lib.connector.services import get_google_drive_credentials

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service(credentials_path: str = None):
    """
    Create and return an authenticated Google Drive service.

    Args:
        credentials_path: Optional path to service account credentials.
            If not provided, uses Connector or env var fallback.

    Returns:
        Google Drive API service instance.
    """
    creds_path = credentials_path or GOOGLE_APPLICATION_CREDENTIALS
    credentials = Credentials.from_service_account_file(
        creds_path,
        scopes=SCOPES,
    )
    service = build("drive", "v3", credentials=credentials)
    return service


def _scan_folder_recursive(service, folder_id, folder_name, processed_ids, stats):
    """
    Recursively scan a folder and its subfolders.

    Args:
        service: Google Drive API service
        folder_id: ID of the folder to scan
        folder_name: Name of the folder (for logging)
        processed_ids: Set of already processed file IDs
        stats: Dict with 'processed' and 'skipped' counters
    """
    logger.info(f"Scanning folder: {folder_name} ({folder_id})")

    # List all items in the folder
    query = f"'{folder_id}' in parents and trashed = false"
    page_token = None

    while True:
        results = (
            service.files()
            .list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType)",
                pageSize=100,
                pageToken=page_token,
            )
            .execute()
        )

        files = results.get("files", [])

        for file in files:
            file_id = file["id"]
            file_name = file["name"]
            mime_type = file.get("mimeType", "")

            # If it's a folder, scan it recursively
            if mime_type == "application/vnd.google-apps.folder":
                _scan_folder_recursive(service, file_id, file_name, processed_ids, stats)
                continue

            # Skip already processed files
            if file_id in processed_ids:
                stats['skipped'] += 1
                logger.debug(f"Skipping already processed file: {file_name}")
                continue

            # Skip non-document files
            if not (file_name.lower().endswith('.pdf') or file_name.lower().endswith('.docx')):
                logger.debug(f"Skipping non-document file: {file_name}")
                continue

            try:
                logger.info(f"Processing file: {file_name} (ID: {file_id})")

                # Download file content
                request = service.files().get_media(fileId=file_id)
                content = request.execute()

                # Extract text using file_parser
                extracted_text = file_parser.extract_text(content, file_name)

                if extracted_text:
                    # Analyze the contract
                    analysis_result = analyze_contract(extracted_text, file_name)
                    logger.info(
                        f"Contract analysis completed for: {file_name} "
                        f"(risk_score: {analysis_result.get('risk_score', 'N/A')})"
                    )

                    # Mark as processed
                    mark_processed(file_id)
                    stats['processed'] += 1
                else:
                    logger.warning(f"No text extracted from file: {file_name}")

            except Exception as e:
                logger.error(f"Error processing file {file_name}: {e}")
                continue

        # Check for more pages
        page_token = results.get("nextPageToken")
        if not page_token:
            break


def run_drive_scan():
    """
    Scan all configured Google Drive folders recursively for new files.

    For each unprocessed file:
    - Download the content
    - Extract text using file_parser
    - Analyze the contract
    - Mark as processed
    """
    try:
        # Always use the absolute path from settings
        credentials_path = GOOGLE_APPLICATION_CREDENTIALS

        # Build folder list from settings
        folder_ids = list(GOOGLE_DRIVE_FOLDER_IDS)

        logger.info(f"Using credentials: {credentials_path}")
        logger.info(f"Scanning {len(folder_ids)} root folder(s) recursively...")

        service = get_drive_service(credentials_path)
        processed_ids = get_processed_ids()

        stats = {'processed': 0, 'skipped': 0}

        for folder_id in folder_ids:
            _scan_folder_recursive(service, folder_id, f"Root-{folder_id[:8]}", processed_ids, stats)

        logger.info(
            f"Drive scan complete. Processed: {stats['processed']}, "
            f"Skipped: {stats['skipped']}"
        )

    except Exception as e:
        logger.error(f"Error during Google Drive scan: {e}")
        raise
