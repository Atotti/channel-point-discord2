from sqlalchemy import Column, Integer, String, Float
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    balance = Column(Float, default=0.0)  # ユーザーの残高を示すフィールド
