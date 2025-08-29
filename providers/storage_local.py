import json
import os
import csv
from pathlib import Path
from typing import Dict, Any, List
import uuid
from datetime import datetime
from io import StringIO

class LocalStorageProvider:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.sessions_dir = self.data_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
    
    def save_session(self, data: Dict[str, Any], session_id: str = None) -> str:
        """セッションデータを保存"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        file_path = self.sessions_dir / f"{session_id}.json"
        data_with_metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "pinned": False,
            "tags": [],
            "data": data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_with_metadata, f, ensure_ascii=False, indent=2)
        
        return session_id
    
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """セッションデータを読み込み"""
        file_path = self.sessions_dir / f"{session_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"セッション {session_id} が見つかりません")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """セッション一覧を取得"""
        sessions = []
        for file_path in self.sessions_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    sessions.append(session_data)
            except Exception as e:
                print(f"セッションファイル {file_path} の読み込みに失敗: {e}")

        # ピン留めを上位、次に作成日時で降順
        # ピン留めを優先し、作成日時は降順（新しいものが上）
        return sorted(
            sessions,
            key=lambda x: (
                x.get("pinned", False),
                x.get("created_at", "")
            ),
            reverse=True,
        )

    def export_sessions_to_csv(self) -> str:
        """保存されたセッションをCSV文字列で出力"""
        sessions = self.list_sessions()
        output = StringIO()
        fieldnames = [
            "session_id",
            "created_at",
            "type",
            "input",
            "output",
            "pinned",
            "tags",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for s in sessions:
            data = s.get("data", {}) or {}
            writer.writerow(
                {
                    "session_id": s.get("session_id"),
                    "created_at": s.get("created_at"),
                    "type": data.get("type"),
                    "input": json.dumps(
                        data.get("input", {}), ensure_ascii=False
                    ),
                    "output": json.dumps(
                        data.get("output", {}), ensure_ascii=False
                    ),
                    "pinned": s.get("pinned", False),
                    "tags": ";".join(s.get("tags", [])),
                }
            )
        return output.getvalue()

    def delete_session(self, session_id: str) -> bool:
        """セッションファイルを削除"""
        file_path = self.sessions_dir / f"{session_id}.json"
        if not file_path.exists():
            return False
        try:
            file_path.unlink()
            return True
        except Exception:
            return False

    def set_pinned(self, session_id: str, pinned: bool) -> bool:
        """ピン留め状態を更新"""
        file_path = self.sessions_dir / f"{session_id}.json"
        if not file_path.exists():
            return False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            content["pinned"] = bool(pinned)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def update_tags(self, session_id: str, tags: List[str]) -> bool:
        """タグを上書き更新"""
        file_path = self.sessions_dir / f"{session_id}.json"
        if not file_path.exists():
            return False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            # 正規化：空白除去、空要素除外、重複排除
            normalized = []
            seen = set()
            for t in tags:
                if not isinstance(t, str):
                    continue
                name = t.strip()
                if not name:
                    continue
                if name in seen:
                    continue
                seen.add(name)
                normalized.append(name)
            content["tags"] = normalized
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def save_data(self, filename: str, data: Dict[str, Any]) -> str:
        """任意データをファイルに保存"""
        file_path = self.data_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename

