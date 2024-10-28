from sqlalchemy.orm import Session
from models import User

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
