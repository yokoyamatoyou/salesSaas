# 目的とゴール

- **最終目標**：GCP上で動く**マルチテナント**の営業特化SaaS（Streamlit UI + 将来的にAPI層）。
- **段階目標**：ローカルでMVPをDocker（仮想化）で起動ファイルからワンコマンド起動、OpenAI APIは環境変数から取得、保存はローカル。
- **必須機能（MVP）**：
  - 事前アドバイス生成（短期/中期・JSON構造）
  - 商談後ふりかえり解析（要約/BANT/反論/次アクション/メール草案）
  - **アイスブレイク・ネタ生成**（ユーザーの“自分のタイプ”+業界ニュースから1行）
  - 3つの軽い追加入力（業界/目的/制約）
  - JSONスキーマで厳格受け取り（UIカードへ表示）

## フェーズ進捗

- [x] フェーズ0：環境準備（Python 3.11 / 仮想化の方針）
- [x] フェーズ1：ドメインモデル & バリデーション
- [x] フェーズ2：LLMアダプタ（OpenAI）
- [x] フェーズ3：アイスブレイク・ネタ生成（自分のタイプ考慮）
- [x] フェーズ4：事前アドバイス生成（UI + サービス）
- [x] フェーズ5：商談後ふりかえり解析
- [x] フェーズ6：ローカル永続化・履歴・テンプレ
- [x] フェーズ7：起動・配布（MVP完了チェック）
- [ ] フェーズ8：GCP移行（シングルテナント→マルチテナント）
- [ ] フェーズ9：Webリサーチ実装（任意→推奨）
- [ ] フェーズ10：品質・セキュリティ

---

# フェーズ0：環境準備（Python 3.11 / 仮想化の方針）

**目的**：開発が迷わない共通土台。

## 指示

1. Python 3.11 を使用。ローカルでは `pyenv`/`venv` のどちらでも可。
2. 仮想化は **Docker** を採用（後でCloud Runへそのまま持ち込み）。
3. リポジトリ初期構成を作成：

```
repo/
  app/                    # Streamlit UI（MVPはUI直呼び）
    pages/
      1_PreAdvice.py
      2_PostReview.py
    components/           # UI部品
    ui.py                 # ルート（サイドバーなど）
  core/                   # ドメイン（Pydanticモデル、バリデーション）
    models.py
    schema.py
    validation.py
  services/               # ユースケース（LLM/アイスブレイク/要約など）
    pre_advisor.py
    post_analyzer.py
    icebreaker.py
  providers/              # インフラ依存（LLM・検索・保存）
    llm_openai.py
    search_provider.py
    storage_local.py
  prompts/                # Jinja2/YAMLなどで管理
    pre_advice.yaml
    post_review.yaml
    icebreaker.yaml
  data/                   # ローカル保存（JSON/添付）
  tests/
    test_validation.py
    test_services.py
    test_icebreaker.py
  Dockerfile
  docker-compose.yml
  requirements.txt
  .env.example
  start_local.sh          # venvでの起動ファイル
  start_docker.sh         # Dockerでの起動ファイル
  Makefile
  README.md
```

4. `requirements.txt`（最低限）

```
streamlit>=1.33
pydantic>=2.7
jinja2>=3.1
httpx>=0.27
python-dotenv>=1.0
openai>=1.40
tenacity>=8.2
pytest>=8.2
pytest-mock>=3.14
```

5. `.env.example`

```
APP_ENV=local
OPENAI_API_KEY=sk-xxxx
DATA_DIR=./data
SEARCH_PROVIDER=none   # none|cse|newsapi 等
CSE_API_KEY=
CSE_CX=
```

6. **Dockerfile（Python 3.11）**

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
ENTRYPOINT ["streamlit", "run", "app/ui.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

7. **docker-compose.yml**（ローカル開発）

```yaml
version: "3.9"
services:
  web:
    build: .
    ports:
      - "8080:8080"
    env_file:
      - .env
    volumes:
      - ./:/app
      - ./data:/app/data
```

8. **起動ファイル**

- `start_docker.sh`

```bash
#!/usr/bin/env bash
set -e
cp -n .env.example .env || true
docker compose up --build
```

- `start_local.sh`

```bash
#!/usr/bin/env bash
set -e
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env || true
streamlit run app/ui.py
```

## テスト（合格条件）

- `./start_docker.sh` で [http://localhost:8080](http://localhost:8080) にUIが表示される。
- `.env` の `OPENAI_API_KEY` 未設定でもUIロードのみは成功し、呼び出し時にバリデーションで警告が出る。

---

# フェーズ1：ドメインモデル & バリデーション

**目的**：UIから渡る入力を厳密に管理し、OR必須（テキスト or URL）などの制約を実装。

## 指示

1. `core/models.py` に Pydantic モデルを定義：
   - `SalesType`（Enum; 9種）
   - `SalesInput`：タイプ、業界、売るもの、説明(Text|URLのXOR)、競合(Text|URLのXOR)、ステージ、目的、制約(list[str])
   - `PreAdviceOutput` / `PostReviewOutput`（後述JSONスキーマを反映）
2. `core/validation.py` に XORチェック（説明/URL、競合/URL）・URL形式チェック・必須チェックを実装。
3. `core/schema.py` に JSON Schema（dict）として出力スキーマを定義（UIが JSON だけを受け取る前提）。

### 出力スキーマ（要約）

```json
// PreAdviceOutput
{
  "short_term": {
    "openers": {"call":"","visit":"","email":""},
    "discovery": ["..."],
    "differentiation": [{"vs":"競合A","talk":"..."}],
    "objections": [{"type":"価格","script":"..."}],
    "next_actions": ["..."],
    "kpi": {"next_meeting_rate": ">=45%", "poc_rate": ">=20%"},
    "summary": "..."
  },
  "mid_term": {"plan_weeks_4_12": ["..."]}
}
```

```json
// PostReviewOutput
{
  "summary": "...",
  "bant": {"budget":"","authority":"","need":"","timeline":""},
  "champ": {"challenges":"","authority":"","money":"","prioritization":""},
  "objections": [{"theme":"価格","details":"...","counter":"..."}],
  "risks": [{"type":"停滞","prob":"medium","reason":"...","mitigation":"..."}],
  "next_actions": ["..."],
  "followup_email": {"subject":"...","body":"..."},
  "metrics_update": {"stage":"...","win_prob_delta":"+5%"}
}
```

## テスト

- `pytest -q` で `test_validation.py` にて：
  - 説明Text/URLのXORが満たされないとエラー。
  - 競合Text/URLのXORが満たされないとエラー。
  - 無効URLはエラー。

---

# フェーズ2：LLMアダプタ（OpenAI）

**目的**：温度・思考の深さ（reasoning.effort）・JSON厳格化を一元管理。

## 指示

1. `providers/llm_openai.py` に以下を実装：
   - `call_llm(prompt: str, mode: Literal["speed","deep","creative"], json_schema: dict) -> dict`
   - `mode` ごとの既定：
     - speed: `temperature=0.3`, `top_p=0.9`, `reasoning.effort="low"`, `max_output_tokens=1200`
     - deep:  `temperature=0.2`, `reasoning.effort="medium"`, `max_output_tokens=2000`
     - creative: `temperature=0.7`, `reasoning.effort="low"`, `max_output_tokens=800`
   - `response_format` に JSON Schema（strict）を渡し、未充足は再試行（tenacityでリトライ）。
2. APIキーは `OPENAI_API_KEY` を読む。未設定時は例外。

## テスト

- `test_services.py` でモック（mocker/monkeypatch）し、`call_llm` がJSONを返すこと、modeごとのパラメータが反映されることを確認。

---

# フェーズ3：アイスブレイク・ネタ生成（自分のタイプ考慮）

**目的**：会話の入口を1行で。タイプ×業界ニュース×トーンを反映。

## 指示

1. `services/icebreaker.py`：
   - 入力：`sales_type: SalesType`, `industry: str`, `company_hint: str|None`, `search_enabled: bool`
   - ロジック：
     - **トーン辞書**：
       - ハンター/チャレンジャー → 前向き・短文・行動促進
       - アナリスト → データ・事実寄り
       - リレーション/ファーマー → 共感ワード＋近況ネタ
       - ストーリーテラー → 具体的小話
       - クローザー → 価値・締めどころの一言
       - コンサル/問題解決 → 課題仮説を促す問い
     - `providers/search_provider.py` 経由で業界ニュース見出しを1〜2本取得（`SEARCH_PROVIDER` が `none` の時はスタブ固定文）。
     - LLMに `icebreaker.yaml` を渡し、**1行×3案** 返却（JSON配列）。
2. UI（PreAdviceページ）に「アイスブレイクを生成」ボタンを設置し、3案のうち1案をコピーしやすく表示。

## テスト / 進捗

- `test_icebreaker.py`：8件合格（検索スタブで固定の見出しを返し、タイプ別に語調が変わることを確認）。
- UI：`app/pages/1_PreAdvice.py` に「❄️ アイスブレイクを生成」導線、会社ヒント、ニュース使用ON/OFF、候補3件の選択表示を追加。
- LLM未設定時：`IcebreakerService` がフォールバック文を返すため、UIは起動可。

---

# フェーズ4：事前アドバイス生成（UI + サービス）

**目的**：短期/中期アクション・トークトラックをJSONで生成しカード表示。

## 指示

1. `prompts/pre_advice.yaml` にSystem/ユーザー差し込み/出力制約を記述。
2. `services/pre_advisor.py`：SalesInputを受け取り、プロンプトをレンダリング→`call_llm(..., mode="speed")`。
3. `app/pages/1_PreAdvice.py`：
   - 入力フォーム（タイプ/業界/売るもの/説明orURL/競合orURL/ステージ/目的/制約）
   - XORバリデーション（`core.validation`）
   - 生成ボタン→結果JSONをカード化（開幕スクリプト/探索質問/差別化/反論/次アクション/KPI/サマリー）
   - 保存：`providers/storage_local.py` で `data/sessions/{uuid}.json` に保存

## テスト

- 手動：ダミー入力で生成→カード表示→保存ファイルが生成される。
- 自動：`test_services.py` でプロンプト→LLMモック→JSONスキーマ適合を検証。

---

# フェーズ5：商談後ふりかえり解析

**目的**：議事録/メモから構造化情報を抽出し、次アクション・メール草案まで返す。

## 指示

1. `prompts/post_review.yaml` を作成（抽出の厳格化・空欄は"未取得"）。
2. `services/post_analyzer.py` を実装：長文入力→`mode="deep"` で解析。
3. `app/pages/2_PostReview.py`：テキストエリア or ファイルアップロード。結果をカード表示。メール草案は「コピー」ボタン。

## テスト

- 自動：要約・BANT・反論など必須キーが埋まるかのスキーマ検証。
- 手動：実サンプルで出力を確認。

## 進捗状況

**✅ 完了**
- `prompts/post_review.yaml`：プロンプトテンプレートと出力スキーマを定義
- `services/post_analyzer.py`：商談内容解析サービスを実装（LLM呼び出し、フォールバック機能含む）
- `app/pages/2_PostReview.py`：商談後解析UIを実装（入力フォーム、結果表示、保存機能）
- `tests/test_post_analyzer.py`：新機能のテストを作成（8件すべて合格）
- 既存テストの修正：`tests/test_services.py`の統合テストを更新

**⚠️ 現在直面している問題**
- Pythonモジュール名の命名規則問題：`app/pages/1_PreAdvice.py`が数字で始まるため、Streamlitアプリケーションが起動できない
- エラー：`SyntaxError: invalid decimal literal` in `app/ui.py` at line 49

**次のステップ**
1. ファイル名変更：`1_PreAdvice.py` → `pre_advice.py`
2. import文の修正
3. アプリケーション起動テスト
4. フェーズ5の動作確認

---

# フェーズ6：ローカル永続化・履歴・テンプレ

**目的**：良かった出力を資産化し、次回レコメンドに活用。

## 指示

1. `providers/storage_local.py`：JSON保存/取得/一覧。
2. UIに「テンプレとして保存」「テンプレから再生成」導線。
3. 役立ち度★と結果編集内容を併記保存（軽い学習ループ）。

## テスト

- 保存→一覧→再生成が通ること。

---

# フェーズ7：起動・配布（MVP完了チェック）

**目的**：ワンコマンド起動、README整備。

## 指示

1. READMEに：
   - 前提（Docker or Python3.11）
   - 起動方法（`./start_docker.sh` または `./start_local.sh`）
   - 環境変数の説明
   - テスト方法（`pytest -q`）
2. Makefile（任意）：`make run`, `make test`, `make lint` など。

## 合格条件

- 新規マシンでも `.env` を用意すれば **起動ファイル1つでMVPが起動**。

### 完了メモ (2025-09-11)
- READMEに前提・起動方法・環境変数・テスト方法を明記
- Makefileに `run`/`docker-run`/`test`/`lint` ターゲットを整備

---

# フェーズ8：GCP移行（シングルテナント→マルチテナント）

**目的**：Cloud Run / Firestore / GCS / Secret Manager で運用。

## 指示

1. **プロジェクト準備**
   - 新規 GCP プロジェクト。APIs 有効化：Cloud Run, Artifact Registry, Firestore(ネイティブ), Secret Manager, Cloud Build, Pub/Sub。
   - Artifact Registry にDocker push。Cloud BuildでCI/CD。
2. **Secrets**
   - `OPENAI_API_KEY` を Secret Manager に登録。Cloud Run に環境変数として注入。
3. **Firestore**（最初はシングルテナント）
   - コレクション：`tenants/{tenant_id}/sessions/{session_id}` 形式に設計（先にスキーマを合わせておく）。
   - `providers/storage_firestore.py` を追加し、`SEARCH_PROVIDER` など設定もFirestoreで上書き可能に。
4. **Cloud Run デプロイ**
   - Dockerイメージを `gcloud run deploy`。ポート8080、最小インスタンス0、同時実行はUI用途に合わせ保守的に。
5. **認証**
   - 段階1：非公開（IAP）or 招待リンクで限定公開。
   - 段階2：Firebase Auth でログイン。ユーザー→`tenant_id` 紐付け。
6. **マルチテナント化**
   - 認証クレームから `tenant_id` を抽出。
   - すべての保存/取得は `tenant_id` を必須に（ガード実装）。
   - Firestore セキュリティルールで `request.auth.token.tenant_id == resource.data.tenant_id` を強制。
   - UI：テナント切替UI（管理者のみ）。
7. **ログ/監視**
   - Cloud Logging/Trace 有効化。個人情報はマスク。
8. **コスト最適化**
   - 長文解析は Pub/Sub + バックグラウンドワーカー（将来）。

## テスト

- ステージング環境でテナントA/Bのデータ分離が保たれること（E2Eチェックリスト）。

---

# フェーズ9：Webリサーチ実装（任意→推奨）

**目的**：アイスブレイクや競合要約に根拠リンクを付与。

## 指示

1. `providers/search_provider.py` にインターフェイス：

```python
class WebSearchProvider:
    async def search(self, query: str, num: int = 3) -> list[dict]:
        ...  # {title, url, snippet}
```

2. 実装例：Google Programmable Search (CSE) / NewsAPI / GCSにキャッシュ。
3. `services/icebreaker.py` と `pre_advisor.py` で、検索結果のURL配列を **出力JSONに同梱**（透明性）。

## テスト

- スタブで固定レスポンスを返し、URLが出力JSONに含まれること。

---

# フェーズ10：品質・セキュリティ

**目的**：実運用に耐える最小限の品質担保。

## 指示

1. PII自動マスキング（メール/電話/氏名）ユーティリティを導入。
2. 監査ログ（誰が/いつ/どの案件を生成したか）。
3. 例外共通ハンドラ（ユーザー向け文言は安全・簡潔）。
4. 回帰テスト：プロンプトのスナップショット（主要キー欠落を検知）。

---

# 付録A：自分のタイプ（9種表示とトーン指針）

- 🏹 ハンター：短文・行動促進・前向き
- 🔒 クローザー：価値訴求→締めの一言
- 🤝 リレーション：共感・近況・柔らかめ
- 🧭 コンサル：課題仮説・問いかけ
- ⚡ チャレンジャー：仮説提示・視点転換
- 📖 ストーリーテラー：具体例・物語
- 📊 アナリスト：事実・データ起点
- 🧩 問題解決：障害除去・次の一歩
- 🌾 ファーマー：長期関係・紹介喚起

---

# 付録B：最小コードスニペット（抜粋）

**（イメージ）**

```python
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODES = {
  "speed": dict(temperature=0.3, top_p=0.9, reasoning_effort="low", max_output_tokens=1200),
  "deep": dict(temperature=0.2, reasoning_effort="medium", max_output_tokens=2000),
  "creative": dict(temperature=0.7, reasoning_effort="low", max_output_tokens=800)
}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def call_llm(prompt: str, mode: str, json_schema: dict) -> dict:
    m = MODES[mode]
    resp = client.chat.completions.create(
        model="gpt-5.1-mini",  # 実際は最新を設定管理
        messages=[{"role":"system","content":"日本のトップ営業コーチ。JSONのみ返答。"},
                  {"role":"user","content":prompt}],
        temperature=m.get("temperature", 0.3),
        top_p=m.get("top_p", 1.0),
        response_format={"type":"json_schema","json_schema":json_schema,"strict":True},
        max_output_tokens=m.get("max_output_tokens", 1200),
        reasoning={"effort": m.get("reasoning_effort", "low")}
    )
    return resp.choices[0].message.parsed  # SDKに合わせて調整
```

**の実行例**

```bash
chmod +x start_docker.sh
./start_docker.sh
```

---

# 設定ガイドライン

- LLMの温度(`temperature`)は **0.0〜2.0** の範囲に自動クランプされる。
- `max_tokens` はモデル上限（現在は **4000 トークン**）を超えないよう自動調整される。

---

# よくある質問（FAQ）

- **Q：仮想化で起動ファイルからMVPを起動できる？**
  - **A：可能。** 本指示書の Docker 化 + `start_docker.sh`（または `start_local.sh`）でワンコマンド起動。Cloud Run もDockerイメージからそのまま起動可。
- **Q：Webリサーチは必須？**
  - A：MVPではスタブ可。将来はCSE/NewsAPIを差し替え可能な`WebSearchProvider`で実装。
- **Q：マルチテナントの分離は？**
  - A：Firestoreで `tenants/{tenant_id}/...` に統一。Authのクレームで必須ガード＋ルール厳格化。

---

# 進捗更新・引継ぎルール

## 進捗記録の仕組み

### 1. `WORKLOG.md` - 直近の作業記録
- **目的**: 現在進行中の作業と直面している問題の詳細記録
- **更新頻度**: 作業セッションごと
- **内容**:
  - 完了した作業
  - 現在直面している問題
  - 試行した解決策
  - 次のステップ
  - 技術的な課題
  - 各作業後の視点レビュー（Python上級エンジニア / UI・UX専門家 / クラウドエンジニア / ユーザー）

### 2. `AGENT.md` - 全体の開発計画と進捗
- **目的**: プロジェクト全体の開発計画、フェーズ別の指示、完了状況
- **更新頻度**: フェーズ完了時、重要な決定時
- **内容**:
  - 各フェーズの完了状況
  - 技術的な決定事項
  - 全体の進捗概要

### 3. 記録の使い分け
- **日常的な作業記録**: `WORKLOG.md`に記録
- **フェーズ完了や重要な決定**: `AGENT.md`に記録
- **問題解決の詳細**: `WORKLOG.md`に記録
- **全体の進捗確認**: `AGENT.md`を参照

### 4. 引継ぎ時の確認ポイント
1. `WORKLOG.md`で現在の作業状況を把握
2. `AGENT.md`で全体の進捗と次のフェーズを確認
3. 直面している問題と試行した解決策を理解
4. 次のステップの計画を確認

---

- 進捗は `docs/PROGRESS.md` に日付/担当/フェーズ/完了・未完/次アクション/メモで記録。
- 重要な決定は `docs/DECISIONS.md`（ADR方式：番号/背景/決定/影響）に記録。
- Issueテンプレ（GitHub）に「再現手順／期待結果／実結果」を必須化。


- 2025-09-10: `Localtest.md`（ローカルテスト指示書）を追加し、各視点を統合した手順を記載。

- 2025-09-11: READMEとMakefileの開発コマンドを文書化し、フェーズ7完了としてPR準備。
