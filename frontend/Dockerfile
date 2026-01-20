# syntax=docker/dockerfile:1

########################
# 1) Build stage
########################
FROM node:20-alpine AS builder
WORKDIR /app

# 의존성 먼저 (캐시 최적화)
COPY package*.json ./
RUN npm ci

# 소스 복사 후 빌드
COPY . .
RUN npm run build


########################
# 2) Runtime stage
########################
FROM nginx:alpine
# dist -> nginx 정적 경로로 복사
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
