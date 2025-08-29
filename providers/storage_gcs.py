import json
import uuid
from datetime import datetime
from typing import Any, Dict, List
import os

from google.cloud import storage


class GCSStorageProvider:
    """Google Cloud Storage based session storage provider"""

    def __init__(self, bucket_name: str, prefix: str = "sessions") -> None:
        if not bucket_name:
            raise ValueError("bucket_name is required")
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.prefix = prefix.rstrip("/") + "/"

    def _blob(self, session_id: str):
        return self.bucket.blob(f"{self.prefix}{session_id}.json")

    def save_session(self, data: Dict[str, Any], session_id: str | None = None) -> str:
        """Save session data to GCS"""
        if session_id is None:
            session_id = str(uuid.uuid4())

        blob = self._blob(session_id)
        data_with_metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "pinned": False,
            "tags": [],
            "data": data,
        }
        blob.upload_from_string(
            json.dumps(data_with_metadata, ensure_ascii=False, indent=2),
            content_type="application/json",
        )
        return session_id

    def load_session(self, session_id: str) -> Dict[str, Any]:
        """Load a session by id"""
        blob = self._blob(session_id)
        if not blob.exists():
            raise FileNotFoundError(f"session {session_id} not found")
        content = blob.download_as_text()
        return json.loads(content)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        sessions: List[Dict[str, Any]] = []
        for blob in self.client.list_blobs(self.bucket, prefix=self.prefix):
            if not blob.name.endswith(".json"):
                continue
            try:
                content = blob.download_as_text()
                sessions.append(json.loads(content))
            except Exception:
                continue
        return sorted(
            sessions,
            key=lambda x: (
                x.get("pinned", False),
                x.get("created_at", ""),
            ),
            reverse=True,
        )

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        blob = self._blob(session_id)
        if not blob.exists():
            return False
        blob.delete()
        return True

    def set_pinned(self, session_id: str, pinned: bool) -> bool:
        """Update pinned state"""
        blob = self._blob(session_id)
        if not blob.exists():
            return False
        try:
            content = json.loads(blob.download_as_text())
            content["pinned"] = bool(pinned)
            blob.upload_from_string(
                json.dumps(content, ensure_ascii=False, indent=2),
                content_type="application/json",
            )
            return True
        except Exception:
            return False

    def update_tags(self, session_id: str, tags: List[str]) -> bool:
        """Overwrite tags"""
        blob = self._blob(session_id)
        if not blob.exists():
            return False
        try:
            content = json.loads(blob.download_as_text())
            normalized: List[str] = []
            seen = set()
            for t in tags:
                if not isinstance(t, str):
                    continue
                name = t.strip()
                if not name or name in seen:
                    continue
                seen.add(name)
                normalized.append(name)
            content["tags"] = normalized
            blob.upload_from_string(
                json.dumps(content, ensure_ascii=False, indent=2),
                content_type="application/json",
            )
            return True
        except Exception:
            return False

    def save_data(self, filename: str, data: Dict[str, Any]) -> str:
        """Save arbitrary data file"""
        blob = self.bucket.blob(f"{self.prefix}{filename}")
        blob.upload_from_string(
            json.dumps(data, ensure_ascii=False, indent=2),
            content_type="application/json",
        )
        return filename
