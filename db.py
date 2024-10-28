from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Docker Composeで設定したDATABASE_URLを環境変数から取得
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemyエンジンの作成
engine = create_engine(DATABASE_URL)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースモデルの作成
Base = declarative_base()
