# Copilot Instructions

## 言語

このリポジトリでは**日本語で回答**すること。コメント・コミットメッセージ・ドキュメントもすべて日本語で記述する。

## コマンド

```bash
# 依存パッケージインストール
uv sync --extra dev

# APIサーバー起動
uv run fastapi dev app/main.py

# Taskiqワーカー起動（別ターミナル）
uv run taskiq worker app.broker:broker app.tasks.sample

# テスト実行
uv run pytest                                             # 全テスト
uv run pytest tests/path/to/test_file.py::test_name -v   # 単体テスト

# Lint / フォーマット
uv run ruff check .
uv run ruff format .
```

## アーキテクチャ

ドメイン駆動構成。責務を明確に分離している：

- **`app/main.py`** — FastAPIアプリ、lifespanハンドラ（`create_db_and_tables()` + Taskiqブローカー起動/停止）、ルーター登録
- **`app/database.py`** — SQLModelエンジン、`create_db_and_tables()`、`get_session()` 依存関係
- **`app/broker.py`** — Taskiq `ListQueueBroker`（Redis）と `RedisAsyncResultBackend` の設定
- **`app/models/`** — SQLModel テーブルクラス（`table=True`）。DBスキーマを定義する
- **`app/schemas/`** — APIのリクエスト/レスポンス用 Pydantic モデル（DB非永続）。命名は `*Create`、`*Read`、`*Update`
- **`app/routers/`** — `APIRouter` モジュール。`main.py` でprefixとtagsを付けてinclude
- **`app/services/`** — ビジネスロジック。`Session` を引数に受け取る関数群
- **`app/tasks/`** — Taskiqタスク関数。`@broker.task` デコレーター付き

## 起動方法

```bash
# ローカル開発（Redisが必要）
docker run -d -p 6379:6379 redis:7-alpine
uv run fastapi dev app/main.py          # APIサーバー
uv run taskiq worker app.broker:broker app.tasks.sample  # ワーカー（別ターミナル）

# Docker Compose でまとめて起動
docker compose up
```

## 主要な規約

**ModelsとSchemasの区別:** `app/models/` は `table=True` のSQLModelクラス（DBテーブル）。`app/schemas/` はAPI I/O用の純粋なPydanticモデル。混在させない。

**依存性注入:** ルーター関数では必ず `session: Session = Depends(get_session)` を使う。ルーターやサービス内で直接 `Session` をインスタンス化しない。

**ルーター登録:** `app/routers/` に新しいルーターを作ったら `app/main.py` でincludeする：
```python
from app.routers import items
app.include_router(items.router, prefix="/items", tags=["items"])
```

**非同期ジョブ:** ジョブ投入時はUUIDを先に生成してDBに保存し、そのIDをタスク関数に渡す。タスク関数内から `app.services.job.update_job_status()` でDB上のステータス・進捗を更新する。

**テストフィクスチャ:** `tests/conftest.py` が提供する2つのフィクスチャを使う：
- `session` — インメモリSQLiteの `Session`（全テーブル作成済み）
- `client` — `get_session` をオーバーライドした `TestClient`

本物のDBには絶対に接続しない。

**環境変数:** `.env.example` を `.env` にコピーして使う。`DATABASE_URL`（SQLite）と `REDIS_URL`（Redis）の2つが必要。
