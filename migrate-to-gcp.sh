#!/bin/bash
# 🚀 Google Cloud移行スクリプト（営業特化SaaS用）
# 使用方法: ./migrate-to-gcp.sh

set -e

# 設定変数（必ず変更してください）
PROJECT_ID="sales-saas-[YOUR-UNIQUE-ID]"
REGION="asia-northeast1"
SERVICE_NAME="sales-saas"
REPOSITORY_NAME="sales-saas-repo"

# 色付きのログ出力
log_info() {
    echo -e "\033[1;34mℹ️  $1\033[0m"
}

log_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

log_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

log_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

# 前提条件のチェック
check_prerequisites() {
    log_info "前提条件をチェック中..."
    
    # gcloud CLIの確認
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLIがインストールされていません。"
        log_error "https://cloud.google.com/sdk/docs/install からインストールしてください。"
        exit 1
    fi
    
    # Dockerの確認
    if ! command -v docker &> /dev/null; then
        log_error "Dockerがインストールされていません。"
        log_error "https://docs.docker.com/get-docker/ からインストールしてください。"
        exit 1
    fi
    
    # プロジェクトIDの確認
    if [[ "$PROJECT_ID" == "sales-saas-[YOUR-UNIQUE-ID]" ]]; then
        log_error "PROJECT_IDを設定してください。"
        log_error "例: sales-saas-2025-08-11"
        exit 1
    fi
    
    log_success "前提条件チェック完了"
}

# プロジェクトの設定
setup_project() {
    log_info "GCPプロジェクトを設定中..."
    
    # プロジェクトの存在確認
    if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
        log_info "プロジェクト $PROJECT_ID を作成中..."
        gcloud projects create "$PROJECT_ID" --name="営業特化SaaS"
    fi
    
    # プロジェクトを選択
    gcloud config set project "$PROJECT_ID"
    
    # 請求アカウントの確認
    BILLING_ACCOUNT=$(gcloud billing accounts list --format="value(ACCOUNT_ID)" --filter="OPEN=true" --limit=1)
    if [[ -z "$BILLING_ACCOUNT" ]]; then
        log_error "有効な請求アカウントが見つかりません。"
        log_error "Google Cloud Consoleで請求を有効化してください。"
        exit 1
    fi
    
    # プロジェクトに請求アカウントをリンク
    gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT"
    
    log_success "プロジェクト設定完了"
}

# 必要なAPIの有効化
enable_apis() {
    log_info "必要なAPIを有効化中..."
    
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        artifactregistry.googleapis.com \
        secretmanager.googleapis.com \
        firestore.googleapis.com \
        cloudresourcemanager.googleapis.com \
        iam.googleapis.com \
        logging.googleapis.com
    
    log_success "API有効化完了"
}

# Artifact Registryの準備
setup_artifact_registry() {
    log_info "Artifact Registryを準備中..."
    
    # リポジトリの存在確認
    if ! gcloud artifacts repositories describe "$REPOSITORY_NAME" --location="$REGION" &> /dev/null; then
        gcloud artifacts repositories create "$REPOSITORY_NAME" \
            --repository-format=docker \
            --location="$REGION" \
            --description="営業特化SaaS用Dockerリポジトリ"
    fi
    
    log_success "Artifact Registry準備完了"
}

# Dockerイメージのビルドとプッシュ
build_and_push_image() {
    log_info "Dockerイメージをビルド中..."
    
    # ローカルでDockerイメージをビルド
    docker build -t "$SERVICE_NAME" .
    
    # イメージのタグ付け
    IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME:latest"
    docker tag "$SERVICE_NAME" "$IMAGE_URI"
    
    # イメージのプッシュ
    log_info "Dockerイメージをプッシュ中..."
    docker push "$IMAGE_URI"
    
    log_success "Dockerイメージのビルドとプッシュ完了"
}

# Cloud Runへのデプロイ
deploy_to_cloud_run() {
    log_info "Cloud Runにデプロイ中..."
    
    IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME:latest"
    
    gcloud run deploy "$SERVICE_NAME" \
        --image="$IMAGE_URI" \
        --platform=managed \
        --region="$REGION" \
        --allow-unauthenticated \
        --port=8080 \
        --memory=2Gi \
        --cpu=1 \
        --max-instances=10 \
        --min-instances=0 \
        --set-env-vars="APP_ENV=production,DATA_DIR=/tmp"
    
    log_success "Cloud Runデプロイ完了"
}

# シークレットの設定
setup_secrets() {
    log_info "シークレットの設定中..."
    
    # OpenAI APIキーの入力
    read -p "OpenAI APIキーを入力してください: " OPENAI_API_KEY
    
    if [[ -n "$OPENAI_API_KEY" ]]; then
        # シークレットの作成
        echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-
        
        # Cloud Runサービスにシークレットを追加
        gcloud run services update "$SERVICE_NAME" \
            --region="$REGION" \
            --set-env-vars="OPENAI_API_KEY=projects/$PROJECT_ID/secrets/openai-api-key/versions/latest"
        
        log_success "シークレット設定完了"
    else
        log_warning "OpenAI APIキーが入力されませんでした。後で手動で設定してください。"
    fi
}

# 動作確認
verify_deployment() {
    log_info "デプロイの動作確認中..."
    
    # サービスのURLを取得
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")
    
    log_success "デプロイ完了！"
    echo ""
    echo "🌐 サービスURL: $SERVICE_URL"
    echo ""
    echo "📋 次のステップ:"
    echo "1. ブラウザで $SERVICE_URL にアクセス"
    echo "2. アプリケーションが正常に動作するか確認"
    echo "3. 必要に応じてシークレットを手動で設定"
    echo ""
}

# メイン処理
main() {
    echo "🚀 営業特化SaaSのGoogle Cloud移行を開始します..."
    echo "プロジェクトID: $PROJECT_ID"
    echo "リージョン: $REGION"
    echo "サービス名: $SERVICE_NAME"
    echo ""
    
    check_prerequisites
    setup_project
    enable_apis
    setup_artifact_registry
    build_and_push_image
    deploy_to_cloud_run
    setup_secrets
    verify_deployment
    
    log_success "🎉 移行が完了しました！"
}

# エラーハンドリング
trap 'log_error "エラーが発生しました。ログを確認してください。"; exit 1' ERR

# スクリプトの実行
main "$@"
