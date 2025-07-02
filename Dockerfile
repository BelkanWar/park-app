# Dockerfile
# 使用官方 Python 映像檔作為基礎
FROM python:3.12.8-slim-bookworm

# 設定工作目錄
WORKDIR /app

# 將 requirements.txt 複製到容器中並安裝依賴
RUN pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile

# 將整個應用程式代碼複製到容器中
COPY . .

# 設定 Flask 應用程式的環境變數
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# 暴露應用程式運行所需的端口 (Cloud Run 預設監聽 8080)
EXPOSE 8080

# 當容器啟動時運行 Flask 應用程式
CMD ["flask", "run", "--port=8080"]
