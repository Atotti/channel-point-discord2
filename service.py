from sqlalchemy.orm import Session
from models import User, Event, Bet

def create_user(db: Session, name: str, balance: float):
    new_user = User(name=name, balance=balance)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_balance(db: Session, user_id: int, new_balance: float):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.balance = new_balance
        db.commit()
        db.refresh(user)
    return user

def create_event(db: Session, title: str, option_1: str, option_2: str):
    new_event = Event(title=title, option_1=option_1, option_2=option_2)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

def place_bet(db: Session, user_id: int, event_id: int, option: str, amount: float):
    user = db.query(User).filter(User.id == user_id).first()
    event = db.query(Event).filter(Event.id == event_id).first()

    if user.balance < amount:
        raise ValueError("残高が不足しています")

    if option not in [event.option_1, event.option_2]:
        raise ValueError("無効な選択肢です")

    user.balance -= amount
    bet = Bet(user_id=user_id, event_id=event_id, option=option, amount=amount)
    db.add(bet)
    db.commit()
    db.refresh(bet)
    return bet

def finalize_event(db: Session, event_id: int, winning_option: str):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event.winning_option is not None:
        raise ValueError("このイベントはすでに確定しています")

    event.winning_option = winning_option
    winning_bets = db.query(Bet).filter(Bet.event_id == event_id, Bet.option == winning_option).all()

    # 払い戻し処理
    for bet in winning_bets:
        payout = bet.amount * 2  # 賭け金の2倍が払い戻し
        user = bet.user
        user.balance += payout

    db.commit()
    return event

def get_user_balance(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    return user.balance

def close_event(db: Session, event_id: int):
    event = db.query(Event).filter(Event.id == event_id).first()
    event.available = False
    db.commit()
    return event

def get_event(db: Session, event_id: int):
    event = db.query(Event).filter(Event.id == event_id).first()
    return event

def get_all_users(db: Session):
    return db.query(User).all()
