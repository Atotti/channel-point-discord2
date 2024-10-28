from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    balance = Column(Float, default=0.0)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    option_1 = Column(String)  # 選択肢1
    option_2 = Column(String)  # 選択肢2
    winning_option = Column(String, nullable=True)  # 勝った方の選択肢
    available = Column(Boolean, default=True)  # イベントが有効かどうか
    bets = relationship("Bet", back_populates="event")

class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    option = Column(String)  # ユーザーが賭けた選択肢
    amount = Column(Float)  # 賭け金額
    event = relationship("Event", back_populates="bets")
    user = relationship("User")
