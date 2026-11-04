import logging
from pathlib import Path
from uuid import uuid4
from typing import Dict, Any, Optional

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Base local upload directory
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class StorageService:
    """Unified Private Storage Service.
    
    Provides private object storage:
    - Azure Blob Storage when AZURE_STORAGE_CONNECTION_STRING is configured.
    - Local private filesystem storage fallback when in non-production environments.
    - Production enforces strict Azure Blob usage with NO silent fallback to local storage.
    """

    def __init__(self):
        self._blob_service_client = None
        self._container_client = None
        self._is_azure = False
        self._init_storage()

    def _init_storage(self):
        is_prod = settings.environment.lower() == "production"
        conn_str = settings.azure_storage_connection_string.strip()

        if is_prod and not conn_str:
            raise RuntimeError(
                "FATAL: Production environment requires AZURE_STORAGE_CONNECTION_STRING. "
                "Silent fallback to local filesystem storage is strictly prohibited in production."
            )

        if conn_str:
            try:
                from azure.storage.blob import BlobServiceClient
                self._blob_service_client = BlobServiceClient.from_connection_string(conn_str)
                self._container_client = self._blob_service_client.get_container_client(
                    settings.azure_storage_container
                )
                if not self._container_client.exists():
                    self._container_client.create_container()
                self._is_azure = True
                logger.info(
                    f"Azure Blob Storage successfully initialized with container '{settings.azure_storage_container}'."
                )
            except Exception as e:
                if is_prod:
                    raise RuntimeError(
                        f"FATAL: Azure Blob Storage initialization failed in production: {e}. "
                        "Fallback to local filesystem storage is disabled in production."
                    ) from e
                logger.warning(
                    f"Azure Blob Storage initialization failed: {e}. Falling back to local storage in '{UPLOAD_DIR}'."
                )
                self._is_azure = False
        else:
            self._is_azure = False
            logger.info(f"Using local private file storage in '{UPLOAD_DIR}'.")

    @property
    def is_azure(self) -> bool:
        return self._is_azure

    def save_file(
        self,
        file_bytes: bytes,
        filename: Optional[str] = None,
        content_type: str = "image/jpeg",
    ) -> Dict[str, str]:
        """Save file bytes to Azure Blob Storage or local storage.
        
        Returns a dict containing:
        - storage_key: unique key/filename
        - file_path: storage URI or local path for retrieval
        - storage_type: 'azure_blob' or 'local'
        """
        is_prod = settings.environment.lower() == "production"
        ext = ".jpg"
        if filename and "." in filename:
            ext = Path(filename).suffix.lower()
        elif "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"

        storage_key = f"{uuid4().hex}{ext}"

        if self._is_azure and self._container_client:
            try:
                from azure.storage.blob import ContentSettings
                blob_client = self._container_client.get_blob_client(storage_key)
                blob_client.upload_blob(
                    file_bytes,
                    overwrite=True,
                    content_settings=ContentSettings(content_type=content_type),
                )
                return {
                    "storage_key": storage_key,
                    "file_path": f"azure://{settings.azure_storage_container}/{storage_key}",
                    "storage_type": "azure_blob",
                }
            except Exception as e:
                if is_prod:
                    raise RuntimeError(
                        f"Failed to upload to Azure Blob Storage in production: {e}. "
                        "Local fallback is prohibited."
                    ) from e
                logger.error(f"Failed to upload to Azure Blob Storage: {e}. Falling back to local save.")

        if is_prod:
            raise RuntimeError(
                "Cannot save file: Storage service is not connected to Azure Blob Storage in production."
            )

        # Local private filesystem storage (development/testing only)
        local_path = UPLOAD_DIR / storage_key
        local_path.write_bytes(file_bytes)
        return {
            "storage_key": storage_key,
            "file_path": str(local_path),
            "storage_type": "local",
        }

    def read_file(self, file_path_or_key: str) -> bytes:
        """Read file bytes from Azure Blob Storage or local storage."""
        if not file_path_or_key:
            raise FileNotFoundError("Empty file path or storage key.")

        # Azure Blob storage URI check
        if file_path_or_key.startswith("azure://") or (self._is_azure and not Path(file_path_or_key).exists()):
            blob_name = file_path_or_key.split("/")[-1]
            if self._container_client:
                blob_client = self._container_client.get_blob_client(blob_name)
                download_stream = blob_client.download_blob()
                return download_stream.readall()

        # Local storage fallback
        local_path = Path(file_path_or_key)
        if not local_path.is_absolute():
            local_path = UPLOAD_DIR / local_path.name

        if not local_path.exists():
            raise FileNotFoundError(f"File not found on storage: {file_path_or_key}")

        return local_path.read_bytes()

    def delete_file(self, file_path_or_key: str) -> bool:
        """Delete file from Azure Blob Storage or local storage."""
        if not file_path_or_key:
            return False

        # Azure Blob Storage
        if file_path_or_key.startswith("azure://") or (self._is_azure and not Path(file_path_or_key).exists()):
            blob_name = file_path_or_key.split("/")[-1]
            try:
                if self._container_client:
                    blob_client = self._container_client.get_blob_client(blob_name)
                    blob_client.delete_blob()
                    return True
            except Exception as e:
                logger.warning(f"Failed to delete blob '{blob_name}': {e}")
                return False

        # Local filesystem
        try:
            local_path = Path(file_path_or_key)
            if not local_path.is_absolute():
                local_path = UPLOAD_DIR / local_path.name
            if local_path.exists() and local_path.is_file():
                local_path.unlink()
                return True
        except Exception as e:
            logger.warning(f"Failed to delete local file '{file_path_or_key}': {e}")
            return False

        return False

    def delete_assessment_files(self, assessment: dict, image_records: list) -> Dict[str, Any]:
        """Clean up all image artifacts associated with an assessment.
        
        Returns a structured deletion audit report:
        - total_expected: total unique file paths targeted
        - deleted_count: number of files successfully deleted
        - failed_paths: list of paths that failed deletion
        - success: boolean indicating if all targeted files were deleted
        """
        target_paths = set()

        # 1. From assessment session document
        images = assessment.get("images", {})
        if isinstance(images, dict):
            for _, view_data in images.items():
                if isinstance(view_data, dict):
                    fp = view_data.get("file_path")
                    if fp:
                        target_paths.add(fp)

        # 2. From assessment_images collection records
        if isinstance(image_records, list):
            for img_rec in image_records:
                if isinstance(img_rec, dict):
                    rec_path = img_rec.get("file_path")
                    if rec_path:
                        target_paths.add(rec_path)

        deleted_count = 0
        failed_paths = []
        for path in target_paths:
            if self.delete_file(path):
                deleted_count += 1
            else:
                failed_paths.append(path)

        success = len(failed_paths) == 0
        if failed_paths:
            logger.warning(
                f"Failed to delete {len(failed_paths)} / {len(target_paths)} files: {failed_paths}"
            )
        else:
            logger.info(f"Successfully deleted all {deleted_count} assessment image files.")

        return {
            "total_expected": len(target_paths),
            "deleted_count": deleted_count,
            "failed_paths": failed_paths,
            "success": success,
        }


# Global singleton storage service instance
storage_service = StorageService()
