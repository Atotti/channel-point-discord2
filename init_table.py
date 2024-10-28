from db import Base, engine
from models import Event, User, Bet

# テーブルの作成
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
