FROM python:3.11-slim

# 안전을 위해 비루트 유저로 실행
RUN useradd -m runner
USER runner
WORKDIR /home/runner

# (선택) PYTHON 안전 옵션
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
