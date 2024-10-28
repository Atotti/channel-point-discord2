from db import Base, engine
from models import User

# テーブルの作成
Base.metadata.create_all(bind=engine)
