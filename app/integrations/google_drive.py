import logging
from io import BytesIO

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from config.settings import (
    GOOGLE_DRIVE_FOLDER_ID,
    GOOGLE_APPLICATION_CREDENTIALS,
    BASE_DIR,
)
from services.contract_analyzer import analyze_contract
from services import file_parser
from memory.processed_files import get_processed_ids, mark_processed

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    """
    Create and return an authenticated Google Drive service.

    Returns:
        Google Drive API service instance.
    """
    credentials = Credentials.from_service_account_file(
        GOOGLE_APPLICATION_CREDENTIALS,
        scopes=SCOPES,
    )
    service = build("drive", "v3", credentials=credentials)
    return service


def run_drive_scan():
    """
    Scan the configured Google Drive folder for new files.

    For each unprocessed file:
    - Download the content
    - Extract text using file_parser
    - Analyze the contract
    - Mark as processed
    """
    try:
        service = get_drive_service()
        processed_ids = get_processed_ids()

        # List files in the configured folder
        query = f"'{GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed = false"
        results = (
            service.files()
            .list(
                q=query,
                fields="files(id, name, mimeType)",
                pageSize=100,
            )
            .execute()
        )

        files = results.get("files", [])
        logger.info(f"Found {len(files)} files in Google Drive folder")

        processed_count = 0
        skipped_count = 0

        for file in files:
            file_id = file["id"]
            file_name = file["name"]
            mime_type = file.get("mimeType", "")

            # Skip already processed files
            if file_id in processed_ids:
                skipped_count += 1
                logger.debug(f"Skipping already processed file: {file_name}")
                continue

            try:
                logger.info(f"Processing file: {file_name} (ID: {file_id})")

                # Download file content
                request = service.files().get_media(fileId=file_id)
                content = request.execute()

                # Extract text using file_parser
                file_stream = BytesIO(content)
                extracted_text = file_parser.extract_text(file_stream, file_name)

                if extracted_text:
                    # Analyze the contract
                    analysis_result = analyze_contract(extracted_text)
                    logger.info(
                        f"Contract analysis completed for: {file_name}"
                    )

                    # Mark as processed
                    mark_processed(file_id)
                    processed_count += 1
                else:
                    logger.warning(f"No text extracted from file: {file_name}")

            except Exception as e:
                logger.error(f"Error processing file {file_name}: {e}")
                continue

        logger.info(
            f"Drive scan complete. Processed: {processed_count}, "
            f"Skipped: {skipped_count}"
        )

    except Exception as e:
        logger.error(f"Error during Google Drive scan: {e}")
        raise
