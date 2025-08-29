# 営業特化SaaS

GCP上で動く**マルチテナント**の営業特化SaaS（Streamlit UI + 将来的にAPI層）。

## 機能

### MVP機能
- **事前アドバイス生成**：短期/中期・JSON構造
- **商談後ふりかえり解析**：要約/BANT/反論/次アクション/メール草案
- **アイスブレイク・ネタ生成**：ユーザーの"自分のタイプ"+業界ニュースから1行
- 3つの軽い追加入力（業界/目的/制約）
- JSONスキーマで厳格受け取り（UIカードへ表示）

### 履歴・UX
- セッション保存（`data/sessions/{uuid}.json`）とSession ID表示
- 履歴ページ（フィルタ/検索/並び替え/ページネーション）
- 再生成・即時再生成（オートラン）
- 複数選択での一括ピン留め/解除・削除
- タグ（色分けバッジ、マルチセレクト絞込、既存タグサジェスト＋新規追加、ドラッグ並び替え）
- モバイル最適化（パディング/ボタン全幅/フォント、タグ並び替えは狭幅で縦方向）

## 前提条件

- Python 3.11
- Docker（推奨）または venv
- OpenAI API Key

## 起動方法

### Dockerでの起動（推奨）

```bash
# 起動ファイルに実行権限を付与
chmod +x start_docker.sh

# 起動
./start_docker.sh
```

### ローカル環境での起動

```bash
# 起動ファイルに実行権限を付与
chmod +x start_local.sh

# 起動
./start_local.sh
```

## 環境変数

`.env`ファイルを作成し、以下の環境変数を設定してください：

```bash
APP_ENV=local
OPENAI_API_KEY=sk-xxxx
DATA_DIR=./data
STORAGE_PROVIDER=local  # local|gcs
GCS_BUCKET_NAME=        # required when STORAGE_PROVIDER=gcs
GCS_PREFIX=sessions     # optional prefix path
SEARCH_PROVIDER=none   # none|cse|newsapi 等
CSE_API_KEY=
CSE_CX=
```

`STORAGE_PROVIDER` を `gcs` に設定する場合は、`GCS_BUCKET_NAME`（必須）と必要に応じて `GCS_PREFIX` を指定してください。ローカルからGCSにアクセスする際は `GOOGLE_APPLICATION_CREDENTIALS` にサービスアカウントJSONのパスを設定します。

## LLMプロバイダのJSONスキーマ対応

`OpenAIProvider.call_llm` に `json_schema` を渡すと、OpenAI API は
`response_format={"type": "json_schema", "json_schema": schema, "strict": True}`
を利用して呼び出されます。スキーマに合わない応答は `ValueError`
として扱われ、呼び出し元で検知できます。

## テスト

```bash
# テスト実行（全体）
pytest -q

# 主要テスト
pytest tests/test_validation.py -q
pytest tests/test_services.py -q
pytest tests/test_icebreaker.py -q
pytest tests/test_storage_local.py -q
```

## プロジェクト構造

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
  env.example
  start_local.sh          # venvでの起動ファイル
  start_docker.sh         # Dockerでの起動ファイル
  README.md
```

## 営業タイプ（9種）

- 🏹 ハンター：短文・行動促進・前向き
- 🔒 クローザー：価値訴求→締めの一言
- 🤝 リレーション：共感・近況・柔らかめ
- 🧭 コンサル：課題仮説・問いかけ
- ⚡ チャレンジャー：仮説提示・視点転換
- 📖 ストーリーテラー：具体例・物語
- 📊 アナリスト：事実・データ起点
- 🧩 問題解決：障害除去・次の一歩
- 🌾 ファーマー：長期関係・紹介喚起

## 開発状況

- [x] フェーズ0：環境準備
- [x] フェーズ1：ドメインモデル & バリデーション
- [x] フェーズ2：LLMアダプタ（OpenAI）
- [x] フェーズ3：アイスブレイク・ネタ生成
- [x] フェーズ4：事前アドバイス生成（UI + サービス）
- [x] フェーズ5：商談後ふりかえり解析
- [x] フェーズ6：ローカル永続化・履歴・テンプレ
- [ ] フェーズ7：起動・配布（MVP完了チェック）
- [ ] フェーズ8：GCP移行（シングルテナント→マルチテナント）
- [ ] フェーズ9：Webリサーチ実装
- [ ] フェーズ10：品質・セキュリティ

## ライセンス

MIT License

