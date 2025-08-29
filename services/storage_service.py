import os
from providers.storage_local import LocalStorageProvider

try:
    from providers.storage_gcs import GCSStorageProvider  # type: ignore
except Exception:  # pragma: no cover
    GCSStorageProvider = None


def get_storage_provider():
    """Return storage provider based on environment"""
    app_env = os.getenv("APP_ENV", "local")
    provider_name = os.getenv("STORAGE_PROVIDER")
    if provider_name:
        provider = provider_name
    elif app_env != "local":
        provider = "gcs"
    else:
        provider = "local"

    if provider == "gcs":
        if GCSStorageProvider is None:
            raise RuntimeError("GCSStorageProvider not available")
        bucket = os.getenv("GCS_BUCKET_NAME")
        if not bucket:
            raise RuntimeError("GCS_BUCKET_NAME environment variable is required for GCS storage")
        prefix = os.getenv("GCS_PREFIX", "sessions")
        if not prefix:
            raise RuntimeError("GCS_PREFIX environment variable is required for GCS storage")
        return GCSStorageProvider(bucket_name=bucket, prefix=prefix)

    data_dir = os.getenv("DATA_DIR", "./data")
    return LocalStorageProvider(data_dir=data_dir)
