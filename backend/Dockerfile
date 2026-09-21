# 构建上下文是仓库根目录（见 docker-compose.yml 的 context: .），
# 这样才能读到根目录的 requirements.txt，并把 backend/ 整体拷进来。
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# requirements.txt 里 pandas==3.0.5 / numpy==2.5.3 这类版本只对 Python 3.14 提供 wheel，
# 所以基础镜像锁 3.14；换成 3.12 会在 pip install 阶段直接找不到版本而失败。
# 先单独拷 requirements，只要它不变，这一层依赖就能被 Docker 缓存复用。
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/backend/

WORKDIR /app/backend

EXPOSE 8000

# app/db/session.py 会从 backend/.env 读 DATABASE_URL，但镜像里刻意不含 .env
# （见仓库根目录 .dockerignore），所以数据库/缓存地址由 compose 的 environment 注入。
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]