FROM python:3.12-slim

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
 && apt-get clean

# 作業ディレクトリ作成
WORKDIR /app

# ファイルコピー
COPY . .

# 必要なライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install opuslib

# 実行コマンド
CMD ["python", "bot.py"]