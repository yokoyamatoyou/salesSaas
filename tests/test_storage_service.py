import pytest
from services import storage_service


class DummyProvider:
    def __init__(self, *args, **kwargs):
        pass


def test_gcs_requires_bucket(monkeypatch):
    monkeypatch.setenv("STORAGE_PROVIDER", "gcs")
    monkeypatch.delenv("GCS_BUCKET_NAME", raising=False)
    monkeypatch.delenv("GCS_PREFIX", raising=False)
    monkeypatch.setattr(storage_service, "GCSStorageProvider", DummyProvider)
    with pytest.raises(RuntimeError) as exc:
        storage_service.get_storage_provider()
    assert "GCS_BUCKET_NAME" in str(exc.value)


def test_gcs_requires_prefix(monkeypatch):
    monkeypatch.setenv("STORAGE_PROVIDER", "gcs")
    monkeypatch.setenv("GCS_BUCKET_NAME", "bucket")
    monkeypatch.setenv("GCS_PREFIX", "")
    monkeypatch.setattr(storage_service, "GCSStorageProvider", DummyProvider)
    with pytest.raises(RuntimeError) as exc:
        storage_service.get_storage_provider()
    assert "GCS_PREFIX" in str(exc.value)


def test_firestore_requires_credentials(monkeypatch):
    monkeypatch.setenv("STORAGE_PROVIDER", "firestore")
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.setenv("FIRESTORE_TENANT_ID", "tenant")
    monkeypatch.setattr(storage_service, "FirestoreStorageProvider", DummyProvider)
    with pytest.raises(RuntimeError) as exc:
        storage_service.get_storage_provider()
    assert "GOOGLE_APPLICATION_CREDENTIALS" in str(exc.value)


def test_firestore_requires_tenant(monkeypatch, tmp_path):
    monkeypatch.setenv("STORAGE_PROVIDER", "firestore")
    credentials = tmp_path / "cred.json"
    credentials.write_text("{}")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(credentials))
    monkeypatch.delenv("FIRESTORE_TENANT_ID", raising=False)
    monkeypatch.setattr(storage_service, "FirestoreStorageProvider", DummyProvider)
    with pytest.raises(RuntimeError) as exc:
        storage_service.get_storage_provider()
    assert "FIRESTORE_TENANT_ID" in str(exc.value)
