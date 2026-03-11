# FastAPI アプリ

FastAPI + SQLModel + Taskiq + Alpine.js で構築した、TODOリストと非同期ジョブ管理機能を持つフルスタックWebアプリケーション。

## 機能

- 🔐 **認証** — JWTによるログイン認証、ユーザーごとのデータ分離
- 📝 **TODOリスト** — 追加・完了切り替え・編集・削除・フィルター
- ⚙️ **ジョブ管理** — 非同期ジョブの投入・進捗監視・キャンセル（リアルタイム更新）

## セットアップ

```bash
# 1. リポジトリをクローン後、環境変数ファイルを用意
cp .env.example .env
# .env の SECRET_KEY を必ず変更してください

# 2. 依存パッケージをインストール
uv sync --extra dev
```

## 起動方法

### Docker Compose（推奨）

```bash
docker compose up
```

Redis・APIサーバー・Taskiqワーカーが一括起動します。

### ローカル手動起動

```bash
# Redisを起動（別途Dockerが必要）
docker run -d -p 6379:6379 redis:7-alpine

# APIサーバー
uv run fastapi dev app/main.py

# Taskiqワーカー（別ターミナル）
uv run taskiq worker app.broker:broker app.tasks.sample
```

## ユーザー登録

管理者がコマンドラインからユーザーを登録します。

```bash
# Docker Compose 環境
docker compose exec api uv run python scripts/create_user.py <email> <password>

# ローカル環境
uv run python scripts/create_user.py <email> <password>
```

## アクセス

| URL | 説明 |
|---|---|
| http://localhost:8000/login.html | ログイン画面 |
| http://localhost:8000 | TODOリスト（要ログイン） |
| http://localhost:8000/jobs.html | ジョブ管理画面（要ログイン） |
| http://localhost:8000/docs | Swagger UI（API仕様） |

## コマンド一覧

```bash
# テスト
uv run pytest                        # 全テスト
uv run pytest --cov=app              # カバレッジ付き
uv run pytest tests/test_auth.py -v  # 認証テストのみ

# Lint / フォーマット
uv run ruff check .
uv run ruff format .
```

## プロジェクト構成

```
app/
  main.py          # FastAPIアプリ・ルーター登録
  broker.py        # Taskiqブローカー（Redis接続設定）
  database.py      # SQLModelエンジン・get_session依存関係
  core/
    deps.py        # JWT認証依存関係（get_current_user）
  models/          # DBテーブル定義（table=True）
  schemas/         # APIリクエスト/レスポンス用Pydanticモデル
  routers/         # APIエンドポイント
  services/        # ビジネスロジック
  tasks/           # Taskiqタスク関数
scripts/
  create_user.py   # ユーザー登録CLIスクリプト
static/
  login.html       # ログイン画面
  index.html       # TODOリストUI（Alpine.js）
  jobs.html        # ジョブ管理UI（Alpine.js）
  app.js           # 共通ユーティリティ（authFetch / テーマ）
tests/
  conftest.py      # pytest フィクスチャ（インメモリSQLite）
  test_auth.py     # 認証APIテスト（9ケース）
  test_jobs.py     # ジョブAPIテスト（11ケース）
  test_todos.py    # TODO APIテスト（6ケース）
docs/              # 設計ドキュメント
```

## 環境変数

| 変数名 | デフォルト | 説明 |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./dev.db` | DB接続文字列 |
| `REDIS_URL` | `redis://localhost:6379` | Redis接続文字列 |
| `SECRET_KEY` | `change-me-in-production` | JWT署名キー（本番では必ず変更） |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWTトークン有効期限（分） |

## ドキュメント

- [要件定義書](docs/要件定義書.md)
- [仕様書](docs/仕様書.md)
- [アーキテクチャ](docs/アーキテクチャ.md)

