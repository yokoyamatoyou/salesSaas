from typing import Any, Dict, List

import pytest

from providers.storage_firestore import FirestoreStorageProvider


class DummyDoc:
    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.data: Dict[str, Any] = {}
        self.exists = False
        self.subcollections: Dict[str, DummyCollection] = {}

    def set(self, data: Dict[str, Any]) -> None:
        self.data = data
        self.exists = True

    def get(self) -> "DummyDoc":
        return self

    def to_dict(self) -> Dict[str, Any]:
        return self.data

    def delete(self) -> None:
        self.exists = False

    def update(self, data: Dict[str, Any]) -> None:
        self.data.update(data)

    def collection(self, name: str) -> "DummyCollection":
        if name not in self.subcollections:
            self.subcollections[name] = DummyCollection()
        return self.subcollections[name]


class DummyCollection:
    def __init__(self):
        self.docs: Dict[str, DummyDoc] = {}

    def document(self, doc_id: str) -> DummyDoc:
        if doc_id not in self.docs:
            self.docs[doc_id] = DummyDoc(doc_id)
        return self.docs[doc_id]

    def stream(self):
        for doc in self.docs.values():
            yield type("Snap", (), {"to_dict": doc.to_dict})()


class DummyClient:
    def __init__(self):
        self.cols: Dict[str, DummyCollection] = {}

    def collection(self, name: str) -> DummyCollection:
        if name not in self.cols:
            self.cols[name] = DummyCollection()
        return self.cols[name]


def _make_provider(mocker) -> FirestoreStorageProvider:
    mocker.patch("providers.storage_firestore.firestore.Client", DummyClient)
    return FirestoreStorageProvider(tenant_id="t1")


def test_save_and_load_session(mocker):
    provider = _make_provider(mocker)
    payload: Dict[str, Any] = {"type": "pre", "input": {}, "output": {}}
    session_id = provider.save_session(payload, user_id="u1", team_id="team1")
    loaded = provider.load_session(session_id)
    assert loaded["session_id"] == session_id
    assert loaded["data"] == payload


def test_set_pinned_and_list_order(mocker):
    provider = _make_provider(mocker)
    id_a = provider.save_session({"type": "pre"}, session_id="a")
    provider.save_session({"type": "post"}, session_id="b")
    assert provider.set_pinned(id_a, True) is True
    sessions: List[Dict[str, Any]] = provider.list_sessions()
    assert sessions[0]["session_id"] == id_a
    assert sessions[0].get("pinned") is True


def test_update_tags(mocker):
    provider = _make_provider(mocker)
    session_id = provider.save_session({"type": "pre"})
    ok = provider.update_tags(session_id, [" A ", "B", "A", "", None])  # type: ignore[list-item]
    assert ok is True
    loaded = provider.load_session(session_id)
    assert loaded.get("tags") == ["A", "B"]


def test_delete_session(mocker):
    provider = _make_provider(mocker)
    session_id = provider.save_session({"type": "post"})
    assert provider.delete_session(session_id) is True
    with pytest.raises(FileNotFoundError):
        provider.load_session(session_id)
