FROM python:3.11-slim

# Docker CLI 설치 (바이너리 직접 다운로드)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then DOCKER_ARCH="x86_64"; \
    elif [ "$ARCH" = "arm64" ]; then DOCKER_ARCH="aarch64"; \
    else DOCKER_ARCH="$ARCH"; fi && \
    curl -fsSL "https://download.docker.com/linux/static/stable/${DOCKER_ARCH}/docker-24.0.7.tgz" | tar -xz -C /tmp && \
    mv /tmp/docker/docker /usr/local/bin/docker && \
    chmod +x /usr/local/bin/docker && \
    rm -rf /tmp/docker && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn pydantic

WORKDIR /app
COPY app /app/app

EXPOSE 8088
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8088"]