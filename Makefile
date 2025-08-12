SHELL := /bin/bash

.PHONY: setup run run-docker test lint format

setup:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r requirements.txt

run:
	streamlit run app/ui.py

run-docker:
	chmod +x start_docker.sh && ./start_docker.sh

test:
	pytest -q

.PHONY: run test lint clean docker-build docker-run

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

# テスト実行（詳細）
test-verbose:
	@echo "テスト実行中（詳細）..."
	pytest -v

# 特定のテストファイル実行
test-validation:
	@echo "バリデーションテスト実行中..."
	pytest tests/test_validation.py -v

test-services:
	@echo "サービステスト実行中..."
	pytest tests/test_services.py -v

test-icebreaker:
	@echo "アイスブレイクテスト実行中..."
	pytest tests/test_icebreaker.py -v

# リンター実行（将来の実装）
lint:
	@echo "リンター実行中..."
	# TODO: flake8, black, mypy などの実装

# クリーンアップ
clean:
	@echo "クリーンアップ中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage

# Dockerイメージビルド
docker-build:
	@echo "Dockerイメージビルド中..."
	docker build -t sales-saas .

# ヘルプ
help:
	@echo "利用可能なコマンド:"
	@echo "  run           - ローカル環境で起動"
	@echo "  docker-run    - Dockerで起動"
	@echo "  test          - テスト実行"
	@echo "  test-verbose  - テスト実行（詳細）"
	@echo "  test-validation - バリデーションテスト実行"
	@echo "  test-services - サービステスト実行"
	@echo "  test-icebreaker - アイスブレイクテスト実行"
	@echo "  lint          - リンター実行"
	@echo "  clean         - クリーンアップ"
	@echo "  docker-build  - Dockerイメージビルド"
	@echo "  help          - このヘルプを表示"

