from db import SessionLocal
from service import create_user, update_balance

# データベースセッションを開く
db = SessionLocal()

# ユーザーを作成
user = create_user(db, name="Alice", balance=100.0)
print(f"Created user: {user.name}, Balance: {user.balance}")

# 残高を更新
user = update_balance(db, user_id=user.id, new_balance=150.0)
print(f"Updated user: {user.name}, New Balance: {user.balance}")

# セッションを閉じる
db.close()
