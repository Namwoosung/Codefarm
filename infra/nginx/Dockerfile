# syntax=docker/dockerfile:1

########################
# 1) Build stage (Vue build)
########################
FROM node:20-alpine AS builder
WORKDIR /app

# 의존성 캐시 최적화
COPY frontend/package*.json ./
RUN npm ci

# 소스 복사 후 빌드
COPY frontend/ ./
RUN npm run build


########################
# 2) Runtime stage (Nginx serve dist)
########################
FROM nginx:alpine

# nginx 설정 복사
COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY infra/nginx/conf.d/ /etc/nginx/conf.d/

# Vue dist 복사
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
