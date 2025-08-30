SHELL := /bin/bash

.PHONY: run docker-run test lint clean docker-build deploy-cloudrun help

# デフォルトターゲット
all: run

# ローカル環境で起動
run:
	@echo "ローカル環境で起動中..."
	./start_local.sh

# Dockerで起動
docker-run:
	@echo "Dockerで起動中..."
	./start_docker.sh

# テスト実行
test:
	@echo "テスト実行中..."
	pytest -q

# 構文チェック
lint:
        @echo "ruff 実行中..."
        ruff check .
        @echo "bandit 実行中..."
        bandit -r core providers services tests

# クリーンアップ
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache .coverage

# Dockerイメージビルド
docker-build:
	docker build -t sales-saas .

# Cloud Run へデプロイ
deploy-cloudrun:
	gcloud run services replace cloudrun/cloudrun.yaml --region=asia-northeast1

# ヘルプ
help:
	@echo "利用可能なコマンド:"
	@echo "  run         - ローカル環境で起動"
	@echo "  docker-run  - Dockerで起動"
	@echo "  test        - テスト実行"
        @echo "  lint        - ruff と bandit によるコードチェック"
	@echo "  clean       - クリーンアップ"
	@echo "  docker-build- Dockerイメージビルド"
	@echo "  deploy-cloudrun- Cloud Run にデプロイ"
	@echo "  help        - このヘルプを表示"
