#!/usr/bin/env python3
"""ユーザー登録CLIスクリプト。

使い方:
    uv run python scripts/create_user.py admin@example.com password123
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.database import create_db_and_tables, engine
from app.models.user import User
from app.services.auth import create_user


def main():
    if len(sys.argv) != 3:
        print("使い方: uv run python scripts/create_user.py <email> <password>")
        sys.exit(1)

    email, password = sys.argv[1], sys.argv[2]

    if len(password) < 8:
        print("エラー: パスワードは8文字以上にしてください")
        sys.exit(1)

    create_db_and_tables()

    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            print(f"エラー: {email} はすでに登録されています")
            sys.exit(1)

        user = create_user(session, email, password)
        print(f"✓ ユーザーを作成しました: {user.email} (id={user.id})")


if __name__ == "__main__":
    main()
