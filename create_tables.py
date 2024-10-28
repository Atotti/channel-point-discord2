from db import Base, engine

# テーブルの作成
Base.metadata.create_all(bind=engine)
