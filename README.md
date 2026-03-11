# FastAPI アプリ

FastAPI + SQLModel + Taskiq + Alpine.js で構築した、TODOリストと非同期ジョブ管理機能を持つフルスタックWebアプリケーション。

## 機能

- 📝 **TODOリスト** — 追加・完了切り替え・編集・削除・フィルター
- ⚙️ **ジョブ管理** — 非同期ジョブの投入・進捗監視・キャンセル（リアルタイム更新）

## セットアップ

```bash
# 1. リポジトリをクローン後、環境変数ファイルを用意
cp .env.example .env

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

## アクセス

| URL | 説明 |
|---|---|
| http://localhost:8000 | TODOリスト |
| http://localhost:8000/jobs.html | ジョブ管理画面 |
| http://localhost:8000/docs | Swagger UI（API仕様） |

## コマンド一覧

```bash
# テスト
uv run pytest                                              # 全テスト
uv run pytest tests/path/to/test_file.py::test_name -v    # 単体テスト

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
  models/          # DBテーブル定義（table=True）
  schemas/         # APIリクエスト/レスポンス用Pydanticモデル
  routers/         # APIエンドポイント
  services/        # ビジネスロジック
  tasks/           # Taskiqタスク関数
static/
  index.html       # TODOリストUI（Alpine.js）
  jobs.html        # ジョブ管理UI（Alpine.js）
tests/
  conftest.py      # pytest フィクスチャ（インメモリSQLite）
docs/              # 設計ドキュメント
```

## 環境変数

| 変数名 | デフォルト | 説明 |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./dev.db` | DB接続文字列 |
| `REDIS_URL` | `redis://localhost:6379` | Redis接続文字列 |

## ドキュメント

- [要件定義書](docs/要件定義書.md)
- [仕様書](docs/仕様書.md)
- [アーキテクチャ](docs/アーキテクチャ.md)

