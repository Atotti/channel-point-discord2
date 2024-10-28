from db import SessionLocal
from service import create_event, place_bet, finalize_event, create_user

db = SessionLocal()

# イベントの作成
event = create_event(db, title="イベント1", option_1="A", option_2="B")
print(f"イベント: {event.title} ({event.option_1} vs {event.option_2})")

# ユーザーの作成
user1 = create_user(db, name="ユーザー1", balance=100.0)
print(f"ユーザー: {user1.name} ({user1.balance} ポイント)")

# ユーザーが賭けを行う
bet = place_bet(db, user_id=user1.id, event_id=event.id, option="A", amount=50.0)
print(f"ベット: {bet.option} に {bet.amount} ドル賭けました")

# ユーザーの残高を確認
print(f"ユーザー: {user1.name} ({user1.balance} ポイント)")

# イベントの勝者を登録して払い戻しを実行
finalized_event = finalize_event(db, event_id=event.id, winning_option="A")
print(f"勝者: {finalized_event.winning_option}")

# ユーザーの残高を確認
print(f"ユーザー: {user1.name} ({user1.balance} ポイント)")

db.close()
