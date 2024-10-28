FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# 環境変数の設定
ENV PYTHONUNBUFFERED 1
ENV DATABASE_URL=postgresql://postgres:password@db:5432/betting_db

# 必要なパッケージをインストール
COPY requirements.txt /tmp/pip-tmp/
RUN pip install --no-cache-dir -r /tmp/pip-tmp/requirements.txt && rm -rf /tmp/pip-tmp

# アプリケーションファイルをコピー
COPY . /app
WORKDIR /app

# アプリケーションの起動コマンド
CMD ["python", "main:app"]
