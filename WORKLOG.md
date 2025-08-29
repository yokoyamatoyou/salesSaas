# Work Log

テスト環境の Python および主要ライブラリのバージョンは各 `### Testing` セクションに記載し、バージョンが変化した場合は次回ログで更新する。
## 2024-04-27
### Task
- Set up work logging files: added WORKLOG.md and updated AGENT.md to document the new logging rule requiring four perspective reviews per task.
  - refs: [AGENT.md, WORKLOG.md] (b780c7a)

### Reviews
1. **Python上級エンジニア視点**: ドキュメントの構文やリンクに問題なし。将来的なメンテナンスの基盤として明確。
2. **UI/UX専門家**: 作業内容とレビュー視点が一目で分かる形式で、追跡しやすい体験を提供。
3. **クラウドエンジニア視点**: ログが整備されたことで、環境移行時の情報共有が容易に。
4. **ユーザー視点**: 開発の透明性が確保され、進捗を安心して追跡できる。

### Testing
- `pytest -q` で 74 件のテストが成功
- Environment: Python 3.12.10, streamlit==1.49.0, pydantic==2.11.7, jinja2==3.1.6, httpx==0.28.1, python-dotenv==1.1.1, openai==1.102.0, tenacity==9.1.2, pytest==8.4.1

## 2025-08-28
### Task
- AGENT.md にフェーズ進捗チェックボックスを追加
  - refs: [AGENT.md] (75baaf1)
- 旧進捗ファイル（進捗.txt）を削除し管理を一本化
  - refs: [進捗.txt] (75baaf1)

### Reviews
1. **Python上級エンジニア視点**: Markdown の構文が正しく、チェックボックスで進捗が一目で把握できる。
2. **UI/UX専門家**: 進捗の可視化により、ファイルを開いた際に現在地が直感的に理解できる。
3. **クラウドエンジニア視点**: 進捗情報を AGENT.md に統合したことで、クラウド移行時の参照が容易になる。
4. **ユーザー視点**: 余計なファイルがなくなり、情報が整理されたことで迷わずに状況を確認できる。

### Testing
- `pytest -q` が 75 件成功
- Environment: Python 3.12.10, streamlit==1.49.0, pydantic==2.11.7, jinja2==3.1.6, httpx==0.28.1, python-dotenv==1.1.1, openai==1.102.0, tenacity==9.1.2, pytest==8.4.1

## 2025-08-29
### Task
- pre_adviceフォームで説明/競合の入力モード切替時に非選択値をクリアし、XORバリデーションエラーを回避するよう修正
  - refs: [app/pages/pre_advice.py] (dddbd4a)

### Reviews
1. **Python上級エンジニア視点**: session_state の管理が明確になり、不要な値が検証に渡らないため保守性が向上。
2. **UI/UX専門家視点**: 入力方式を切り替えても隠れた値でエラーにならず、ユーザーが混乱しない。
3. **クラウドエンジニア視点**: フォームデータが最小化され、無駄なセッション情報が送信されないためリソース効率が良い。
4. **ユーザー視点**: 入力ミスの自己修正が不要になり、スムーズにアドバイス生成まで進められる。

### Testing
- `pytest -q` で 75 件のテストが成功
- Environment: Python 3.12.10, streamlit==1.49.0, pydantic==2.11.7, jinja2==3.1.6, httpx==0.28.1, python-dotenv==1.1.1, openai==1.102.0, tenacity==9.1.2, pytest==8.4.1

## 2025-08-30
### Task
- PostAnalyzerService が環境変数または設定マネージャーから API キーを取得し、共有 OpenAIProvider を再利用するよう修正
  - refs: [services/post_analyzer.py] (8321c16)
- API キー有無で初期化が成功することを確認するユニットテストを追加
  - refs: [tests/test_post_analyzer.py] (8321c16)

### Reviews
1. **Python上級エンジニア視点**: Singleton の導入で不要な初期化が避けられ、エラーハンドリングも改善された。
2. **UI/UX専門家視点**: API キー欠如時に警告ログが出ることで、ユーザーへのフィードバックが明確になった。
3. **クラウドエンジニア視点**: 環境変数による設定が標準化され、デプロイ環境での秘密管理が容易に。
4. **ユーザー視点**: API キーがない場合でもサービスがフォールバックするため、最低限の機能が維持され安心できる。

### Testing
- `pytest -q` で 75 件のテストが成功
- Environment: Python 3.12.10, streamlit==1.49.0, pydantic==2.11.7, jinja2==3.1.6, httpx==0.28.1, python-dotenv==1.1.1, openai==1.102.0, tenacity==9.1.2, pytest==8.4.1

## 2025-08-31
### Task
 - pre_advice ページで `streamlit` を明示的にインポートし、依存関係の順序を整理
  - refs: [app/pages/pre_advice.py]

### Reviews
1. **Python上級エンジニア視点**: 標準ライブラリ、サードパーティ、ローカルの順に整理され読みやすくなった。
2. **UI/UX専門家視点**: 起動時のエラーが解消され、ユーザーがフォームに到達しやすい。
3. **クラウドエンジニア視点**: 明示的な依存管理により、本番環境でのデプロイが安定。
4. **ユーザー視点**: フォームが問題なく表示され、事前アドバイス生成までスムーズに進める。

### Testing
- `pytest -q` で 81 件のテストが成功
- Environment: Python 3.12.10, streamlit==1.49.0, pydantic==2.11.7, jinja2==3.1.6, httpx==0.28.1, python-dotenv==1.1.1, openai==1.102.0, tenacity==9.1.2, pytest==8.4.1
