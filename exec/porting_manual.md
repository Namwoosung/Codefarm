# 포팅 매뉴얼 (Porting Manual)

> **프로젝트명**: CodeFarm  
> **팀**: SSAFY B109  
> **도메인**: https://i14b109.p.ssafy.io  
> **최종 수정일**: 2025-02-09

---

## 목차

1. [프로젝트 개요 및 아키텍처](#1-프로젝트-개요-및-아키텍처)
2. [사용 제품 및 버전 정보](#2-사용-제품-및-버전-정보)
3. [빌드 시 사용되는 환경 변수](#3-빌드-시-사용되는-환경-변수)
4. [빌드 및 배포 절차](#4-빌드-및-배포-절차)
5. [서버 배포 구성 (Docker Compose)](#5-서버-배포-구성-docker-compose)
6. [배포 시 특이사항](#6-배포-시-특이사항)
7. [DB 접속 정보 및 프로퍼티 파일 목록](#7-db-접속-정보-및-프로퍼티-파일-목록)
8. [외부 서비스 정보](#8-외부-서비스-정보)

---

## 1. 프로젝트 개요 및 아키텍처

### 1.1 서비스 소개

**CodeFarm**은 알고리즘 학습 플랫폼으로, 코드 실행·AI 기반 힌트·피드백 등의 기능을 제공합니다.

### 1.2 시스템 아키텍처

```
                        ┌─────────────────────────────────┐
                        │         Nginx (리버스 프록시)      │
                        │   - HTTPS (Let's Encrypt)        │
                        │   - 포트: 80/443                  │
                        └────────────┬────────────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
    ┌──────▼──────┐          ┌───────▼──────┐          ┌───────▼──────┐
    │  Frontend   │          │   Backend    │          │  Execution   │
    │  (Vue 3)    │          │ (Spring Boot)│          │  (FastAPI)   │
    │  SPA 정적파일│          │  포트: 8080   │          │  포트: 8088   │
    └─────────────┘          └──────┬───────┘          └──────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
             ┌──────▼──┐    ┌──────▼──┐    ┌───────▼───────┐
             │PostgreSQL│    │  Redis  │    │   Feedback    │
             │ 포트:5432 │    │포트:6379│    │   (FastAPI)   │
             └──────────┘    └─────────┘    │   포트: 8089   │
                                            └───────────────┘
                                                    
                              ┌──────────────────┐
                              │   Inference (AI)  │
                              │   (FastAPI)       │
                              │   Elice 컨테이너   │
                              └──────────────────┘
```

### 1.3 마이크로서비스 구성

| 서비스 | 역할 | 포트 | 기술 스택 |
|--------|------|------|-----------|
| **Backend (API)** | REST API, 비즈니스 로직, 인증 | 8080 | Spring Boot 3.5.9, Java 17 |
| **Frontend (Web)** | SPA 클라이언트 | 80/443 (Nginx) | Vue 3.5.26, Vite 7.3.0 |
| **Execution** | 코드 실행 엔진 | 8088 | FastAPI, Python 3.11, Docker-in-Docker |
| **Feedback** | AI 피드백 생성 | 8089 | FastAPI, Python 3.11, GMS API (GPT-4o-mini) |
| **Inference** | AI 힌트 생성 (GPU) | - | FastAPI, Python 3.11, PyTorch 2.7, Transformers |
| **PostgreSQL** | 메인 데이터베이스 | 5432 | PostgreSQL 16 Alpine |
| **Redis** | 캐시/세션 | 6379 | Redis 7 Alpine |

---

## 2. 사용 제품 및 버전 정보

### 2.1 개발 환경 (IDE)

| 구분 | 버전 |
|------|------|
| IntelliJ IDEA | 2024.x 이상 권장 |
| VS Code / Cursor | 최신 버전 |
| Git | 2.40+ |

### 2.2 Backend

| 구분 | 제품/기술 | 버전 |
|------|-----------|------|
| **JDK** | Eclipse Temurin (OpenJDK) | **17** |
| **빌드 도구** | Gradle | **9.2.1** |
| **프레임워크** | Spring Boot | **3.5.9** |
| **WAS** | 내장 Tomcat (Spring Boot) | Spring Boot 내장 |
| **ORM** | Hibernate / Spring Data JPA | Spring Boot 종속 |
| **QueryDSL** | QueryDSL JPA | **5.0.0** (jakarta) |
| **보안** | Spring Security + JWT | jjwt **0.11.5** |
| **DB 드라이버** | PostgreSQL JDBC | Spring Boot 종속 |
| **캐시** | Spring Data Redis (Lettuce) | Spring Boot 종속 |
| **HTTP 클라이언트** | Spring WebFlux (WebClient) | Spring Boot 종속 |
| **유틸** | Lombok, Jackson | Spring Boot 종속 |

### 2.3 Frontend

| 구분 | 제품/기술 | 버전 |
|------|-----------|------|
| **런타임** | Node.js | **20.19.0+** 또는 **22.12.0+** |
| **프레임워크** | Vue.js | **3.5.26** |
| **빌드 도구** | Vite | **7.3.0** |
| **라우터** | Vue Router | **4.6.4** |
| **상태관리** | Pinia | **3.0.4** |
| **HTTP** | Axios | **1.13.3** |
| **CSS** | TailwindCSS | **4.1.18** |
| **UI 라이브러리** | DaisyUI | **5.5.14** |
| **UI 컴포넌트** | PrimeVue | **4.5.4** |
| **코드 에디터** | Monaco Editor | **0.55.1** |
| **터미널** | @xterm/xterm | **6.0.0** |
| **마크다운** | Marked | **17.0.1** |

### 2.4 Execution 서비스 (코드 실행)

| 구분 | 제품/기술 | 버전 |
|------|-----------|------|
| **언어** | Python | **3.11** |
| **프레임워크** | FastAPI | 최신 |
| **ASGI 서버** | Uvicorn | 최신 |
| **컨테이너** | Docker-in-Docker | - |

### 2.5 Feedback 서비스

| 구분 | 제품/기술 | 버전 |
|------|-----------|------|
| **언어** | Python | **3.11** |
| **프레임워크** | FastAPI | 최신 |
| **ASGI 서버** | Uvicorn | 최신 |
| **HTTP 클라이언트** | httpx | 최신 |
| **AI 모델** | GMS API (GPT-4o-mini) | - |

### 2.6 Inference 서비스 (AI 힌트)

| 구분 | 제품/기술 | 버전 |
|------|-----------|------|
| **언어** | Python | **3.11** |
| **프레임워크** | FastAPI | **0.128.0** |
| **ML 프레임워크** | PyTorch | **2.7.0+cu128** |
| **NLP** | Transformers (HuggingFace) | **4.56.2** |
| **최적화** | Unsloth, PEFT, BitsAndBytes | 2025.10.8, 0.18.1, 0.49.1 |
| **GPU** | CUDA | **12.8** |

### 2.7 인프라

| 구분 | 제품/기술 | 버전 |
|------|-----------|------|
| **웹 서버** | Nginx | Alpine (최신) |
| **SSL 인증서** | Let's Encrypt (Certbot) | - |
| **데이터베이스** | PostgreSQL | **16** Alpine |
| **캐시** | Redis | **7** Alpine |
| **컨테이너** | Docker + Docker Compose | 최신 |
| **CI/CD** | GitLab CI/CD | - |
| **이미지 레지스트리** | Docker Hub | - |
| **보안 스캔** | Trivy | - |
| **서버** | AWS EC2 | - |
| **GPU 서버** | Elice 컨테이너 | - |

---

## 3. 빌드 시 사용되는 환경 변수

### 3.1 Backend 환경 변수

`.env` 파일 또는 Docker 환경 변수로 설정합니다.

| 환경 변수 | 설명 | 예시 값 |
|-----------|------|---------|
| `SPRING_PROFILES_ACTIVE` | 활성 프로필 (dev/prod) | `dev` |
| `TZ` | 타임존 | `Asia/Seoul` |
| **[데이터베이스]** | | |
| `POSTGRES_HOST` | PostgreSQL 호스트 | `localhost` |
| `POSTGRES_PORT` | PostgreSQL 포트 | `15432` |
| `POSTGRES_NAME` | 데이터베이스 이름 | `codefarm` |
| `POSTGRES_USER` | DB 사용자명 | `farmer` |
| `POSTGRES_PASSWORD` | DB 비밀번호 | `(보안 정보)` |
| **[Redis]** | | |
| `REDIS_HOST` | Redis 호스트 | `localhost` |
| `REDIS_PORT` | Redis 포트 | `16379` |
| **[JWT]** | | |
| `JWT_SECRET_KEY` | JWT 서명 비밀키 (Base64) | `(보안 정보)` |
| `JWT_ACCESS_EXPIRATION` | Access Token 만료시간 (ms) | `6048000000` |
| `JWT_REFRESH_EXPIRATION` | Refresh Token 만료시간 (ms) | `6048000000` |
| **[로깅]** | | |
| `SHOW_SQL` | SQL 출력 여부 | `false` |
| `FORMAT_SQL` | SQL 포맷팅 여부 | `false` |
| `LOG_SQL` | SQL 로그 레벨 | `DEBUG` |
| `LOG_PARAM` | 파라미터 로그 레벨 | `TRACE` |
| **[외부 서비스 연동]** | | |
| `EXEC_SERVER_BASE_URL` | Execution 서버 URL | `http://execution:8088` |
| `FEEDBACK_SERVER_BASE_URL` | Feedback 서버 URL | `http://feedback:8089` |
| `FEEDBACK_SERVER_TOKEN` | Feedback 서버 인증 토큰 | `(보안 정보)` |
| `HINT_SERVER_BASE_URL` | AI 힌트 서버 URL | `(서버 URL)` |
| `HINT_SERVER_PORT` | AI 힌트 서버 포트 | `(포트)` |
| `HINT_SERVER_TOKEN` | AI 힌트 서버 인증 토큰 | `(보안 정보)` |

### 3.2 Frontend 환경 변수

`.env.development` 또는 `.env.production` 파일로 설정합니다.

| 환경 변수 | 설명 | 예시 값 |
|-----------|------|---------|
| `VITE_API_BASE_URL` | API 서버 기본 URL | `https://i14b109.p.ssafy.io/api/v1` |

### 3.3 CI/CD 환경 변수 (GitLab CI/CD)

GitLab > Settings > CI/CD > Variables에 등록합니다.

| 환경 변수 | 설명 |
|-----------|------|
| `DOCKERHUB_USERNAME` | Docker Hub 사용자명 |
| `DOCKERHUB_TOKEN` | Docker Hub 접근 토큰 |
| `SSH_KEY` | 배포 서버 SSH 키 (File 타입) |
| `HOST` | 배포 대상 서버 호스트 |
| `USER` | 배포 서버 SSH 사용자명 |

---

## 4. 빌드 및 배포 절차

### 4.1 로컬 개발 환경 구성

#### Backend

```bash
# 1. JDK 17 설치 확인
java -version

# 2. 프로젝트 클론
git clone <GITLAB_REPO_URL>
cd CODEFARM/backend

# 3. 환경 변수 설정
# src/main/resources/.env 파일에 환경 변수 설정 (3.1절 참고)

# 4. 빌드 및 실행
./gradlew bootRun
# 또는
./gradlew bootJar
java -jar build/libs/codefarm-0.0.1-SNAPSHOT.jar
```

#### Frontend

```bash
# 1. Node.js 20.19+ 설치 확인
node -v

# 2. 의존성 설치
cd CODEFARM/frontend
npm install

# 3. 환경 변수 설정
# .env.development 파일 확인/수정

# 4. 개발 서버 실행
npm run dev

# 5. 프로덕션 빌드
npm run build
```

#### Execution 서비스

```bash
cd CODEFARM/execution

# Docker 이미지 빌드 및 실행
docker build -t execution .
docker run -p 8088:8088 -v /var/run/docker.sock:/var/run/docker.sock execution
```

#### Feedback 서비스

```bash
cd CODEFARM/feedback

# 의존성 설치 및 실행
pip install -r requirements.txt
uvicorn app.app:app --host 0.0.0.0 --port 8089

# 또는 Docker
docker build -t feedback .
docker run -p 8089:8089 feedback
```

#### Inference 서비스

```bash
cd CODEFARM/inference

# GPU 환경 필요 (CUDA 12.8)
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu128

# 모델 파일 준비 (label_model, text_model)
# models/ 디렉토리에 모델 배치

uvicorn app:app --host 0.0.0.0 --port 8000
```

### 4.2 Docker 빌드

#### Backend Docker 빌드

```bash
# 멀티 스테이지 빌드 (gradle:9.2.1-jdk17-alpine → eclipse-temurin:17-jre-alpine)
docker build -t backend:latest -f backend/Dockerfile backend
```

#### Frontend (Nginx) Docker 빌드

```bash
# 멀티 스테이지 빌드 (node:20-alpine → nginx:alpine)
docker build -t web:latest -f infra/nginx/Dockerfile .
```

#### Execution Docker 빌드

```bash
docker build -t execution:latest -f execution/Dockerfile execution
```

#### Feedback Docker 빌드

```bash
docker build -t feedback:latest -f feedback/Dockerfile feedback
```

### 4.3 CI/CD 파이프라인 (GitLab CI/CD)

`.gitlab-ci.yml` 기반으로 자동 빌드 및 배포가 수행됩니다.

#### 파이프라인 스테이지

```
build → test → security → deploy → inference
```

| 스테이지 | 작업 | 트리거 조건 |
|----------|------|-------------|
| **build** | Docker 이미지 빌드 & Docker Hub 푸시 | develop/main 브랜치 push |
| **test** | 테스트 실행 | MR 또는 feature/infra/fix 브랜치 |
| **security** | Trivy 보안 스캔 (HIGH/CRITICAL) | MR 또는 develop/main 브랜치 |
| **deploy** | SSH로 서버에 배포 스크립트 실행 | develop: 자동 / main: 수동 |
| **inference** | Elice 컨테이너에 Inference 배포 | develop/main + inference/** 변경 시 |

#### 빌드 대상

| 이미지 | Dockerfile 경로 | 컨텍스트 |
|--------|-----------------|----------|
| `backend` | `backend/Dockerfile` | `backend/` |
| `web` | `infra/nginx/Dockerfile` | `.` (루트) |
| `execution` | `execution/Dockerfile` | `execution/` |
| `feedback` | `feedback/Dockerfile` | `feedback/` |

#### 배포 흐름

1. **develop 브랜치** push → 자동 빌드 → 자동 배포 (dev 환경)
2. **main 브랜치** push → 자동 빌드 → **수동** 배포 (prod 환경)

배포 스크립트 경로 (서버):
- Foundation (execution + feedback): `/srv/app/scripts/deploy_foundation.sh`
- Server (backend + web): `/srv/app/scripts/deploy_server.sh`

---

## 5. 서버 배포 구성 (Docker Compose)

### 5.1 서버 디렉토리 구조

배포 서버 (`/srv/app/`) 의 구조는 다음과 같습니다.

```
/srv/app/
├── .env                              # 공통 환경 변수 파일
├── .current_image_tag_dev            # 현재 dev 배포 이미지 태그
├── .current_image_tag_prod           # 현재 prod 배포 이미지 태그
├── .current_image_tag_foundation     # 현재 foundation 배포 이미지 태그
├── .previous_image_tag_dev           # 이전 dev 이미지 태그 (롤백용)
├── .previous_image_tag_prod          # 이전 prod 이미지 태그 (롤백용)
├── .previous_image_tag_foundation    # 이전 foundation 이미지 태그 (롤백용)
├── docker/
│   └── runner/
│       └── python/
│           └── Dockerfile            # Python 코드 실행용 Docker 이미지
├── docker-compose.db.yml             # DB (PostgreSQL + Redis)
├── docker-compose.dev.yml            # 개발 환경 (backend + web)
├── docker-compose.prod.yml           # 프로덕션 환경 (backend + web)
├── docker-compose.exec.yml           # Execution 서비스
├── docker-compose.feedback.yml       # Feedback 서비스
├── letsencrypt-webroot/              # Let's Encrypt 인증용
└── scripts/
    ├── deploy_foundation.sh          # DB + Execution + Feedback 배포
    ├── deploy_server.sh              # Backend + Web 배포
    ├── healthcheck.sh                # 헬스체크 스크립트
    └── rollback.sh                   # 롤백 스크립트
```

### 5.2 Docker Compose 파일 구성

서비스는 여러 개의 Docker Compose 파일로 분리되어 있으며, 공통 네트워크 `appnet`을 통해 통신합니다.

#### 5.2.1 docker-compose.db.yml (데이터베이스)

```yaml
services:
  postgres:
    container_name: postgres
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      TZ: ${TZ}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - appnet
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 8s
      timeout: 3s
      retries: 3

  redis:
    container_name: redis
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes", "--maxmemory", "4gb", "--maxmemory-policy", "volatile-lru"]
    volumes:
      - redisdata:/data
    ports:
      - "6379:6379"
    networks:
      - appnet
    restart: unless-stopped

networks:
  appnet:
    driver: bridge
    external: true

volumes:
  pgdata:
  redisdata:
```

- PostgreSQL 16 Alpine, Redis 7 Alpine 사용
- Redis: AOF 영속성, 최대 메모리 4GB, volatile-lru 정책
- 데이터 볼륨 `pgdata`, `redisdata`로 영속성 보장

#### 5.2.2 docker-compose.prod.yml (프로덕션 — Backend + Web)

```yaml
services:
  api:
    container_name: api-prod
    image: ${DOCKERHUB_USERNAME}/backend:${IMAGE_TAG}
    expose:
      - "8080"
    environment:
      SPRING_PROFILES_ACTIVE: ${SPRING_PROFILES_ACTIVE}
      SPRING_DATASOURCE_URL: jdbc:postgresql://${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_NAME}?connectTimeout=10&socketTimeout=10
      SPRING_DATASOURCE_USERNAME: ${POSTGRES_USER}
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_PASSWORD}
      SPRING_DATA_REDIS_HOST: ${REDIS_HOST}
      SPRING_DATA_REDIS_PORT: ${REDIS_PORT}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      JWT_ACCESS_EXPIRATION: ${JWT_ACCESS_EXPIRATION}
      JWT_REFRESH_EXPIRATION: ${JWT_REFRESH_EXPIRATION}
      SHOW_SQL: ${SHOW_SQL}
      FORMAT_SQL: ${FORMAT_SQL}
      LOG_SQL: ${LOG_SQL}
      LOG_PARAM: ${LOG_PARAM}
      EXEC_SERVER_BASE_URL: ${EXEC_SERVER_BASE_URL}
      FEEDBACK_SERVER_BASE_URL: ${FEEDBACK_SERVER_BASE_URL}
      FEEDBACK_SERVER_TOKEN: ${FEEDBACK_SERVER_TOKEN}
      HINT_SERVER_TOKEN: ${HINT_SERVER_TOKEN}
      HINT_SERVER_BASE_URL: ${HINT_SERVER_BASE_URL}
      HINT_SERVER_PORT: ${HINT_SERVER_PORT}
    networks:
      - appnet
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/actuator/health || exit 1"]
      interval: 8s
      timeout: 3s
      retries: 3

  web:
    container_name: web-prod
    image: ${DOCKERHUB_USERNAME}/web:${IMAGE_TAG}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot:ro
    networks:
      - appnet
    restart: unless-stopped
```

- Backend: `expose: 8080` (내부 네트워크에서만 접근, Nginx가 프록시)
- Web(Nginx): 80/443 포트 바인딩, Let's Encrypt 인증서 읽기전용 마운트
- Actuator `/health` 엔드포인트로 헬스체크

#### 5.2.3 docker-compose.exec.yml (Execution 서비스)

```yaml
services:
  execution:
    container_name: execution
    image: ${DOCKERHUB_USERNAME}/execution:${IMAGE_TAG}
    expose:
      - "8088"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp:/tmp
    restart: unless-stopped
    networks:
      - appnet
```

- Docker 소켓 마운트로 Docker-in-Docker 코드 실행
- `/tmp` 마운트로 임시 파일 공유

#### 5.2.4 docker-compose.feedback.yml (Feedback 서비스)

```yaml
services:
  feedback:
    container_name: feedback
    image: ${DOCKERHUB_USERNAME}/feedback:${IMAGE_TAG}
    environment:
      GMS_API_KEY: ${GMS_API_KEY}
      GMS_MODEL: ${GMS_MODEL}
      REQUIRE_SERVER_TOKEN: ${REQUIRE_SERVER_TOKEN}
      REPORT_SERVER_TOKEN: ${REPORT_SERVER_TOKEN}
    expose:
      - "8089"
    restart: unless-stopped
    networks:
      - appnet
```

- GMS API 키와 모델명을 환경 변수로 주입
- 서버 간 인증 토큰 사용

### 5.3 Docker 네트워크

모든 서비스는 `appnet`이라는 **외부(external) 브릿지 네트워크**를 공유합니다.

```bash
# 네트워크 생성 (최초 1회)
docker network create appnet
```

서비스 간 통신은 컨테이너 이름으로 수행됩니다:
- `api` → `postgres:5432` (DB 접속)
- `api` → `redis:6379` (캐시)
- `api` → `execution:8088` (코드 실행)
- `api` → `feedback:8089` (피드백)
- `web` → `api:8080` (Nginx → Backend 프록시)

### 5.4 배포 스크립트

#### 5.4.1 Foundation 배포 (`deploy_foundation.sh`)

DB + Execution + Feedback 서비스를 배포합니다.

```
실행: DOCKERHUB_USERNAME=... DOCKERHUB_TOKEN=... IMAGE_TAG=... bash /srv/app/scripts/deploy_foundation.sh
```

**처리 흐름:**
1. 필수 환경 변수 검증 (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `IMAGE_TAG`)
2. 필요 파일 존재 확인 (`docker-compose.db.yml`, `docker-compose.exec.yml`, `docker-compose.feedback.yml`, `.env`)
3. `appnet` 네트워크 생성 (미존재 시)
4. Docker Hub 로그인
5. 현재 이미지 태그 백업 (`.current_image_tag_foundation` → `.previous_image_tag_foundation`)
6. 새 이미지 태그 저장
7. `docker compose pull` → `docker compose up -d --remove-orphans`
8. 헬스체크 실행

#### 5.4.2 Server 배포 (`deploy_server.sh`)

Backend + Web 서비스를 배포합니다.

```
실행: DOCKERHUB_USERNAME=... DOCKERHUB_TOKEN=... IMAGE_TAG=... bash /srv/app/scripts/deploy_server.sh <dev|prod>
```

**처리 흐름:**
1. 환경 인자 검증 (`dev` 또는 `prod`)
2. 해당 환경의 `docker-compose.{env}.yml` 파일 사용
3. 이하 Foundation 배포와 동일한 흐름

#### 5.4.3 롤백

이전 이미지 태그가 `.previous_image_tag_*` 파일에 저장되어 있어, `rollback.sh` 스크립트로 이전 버전으로 롤백 가능합니다.

### 5.5 서버 환경 변수 (.env)

서버의 `/srv/app/.env` 파일에 모든 환경 변수를 통합 관리합니다.

| 환경 변수 | 설명 |
|-----------|------|
| **[공통]** | |
| `DOCKERHUB_USERNAME` | Docker Hub 사용자명 |
| `IMAGE_TAG` | 배포 이미지 태그 (CI/CD에서 주입) |
| `TZ` | 타임존 (`Asia/Seoul`) |
| **[PostgreSQL]** | |
| `POSTGRES_DB` | DB 이름 (`codefarm`) |
| `POSTGRES_HOST` | DB 호스트 (Docker 내부: `postgres`) |
| `POSTGRES_PORT` | DB 포트 (`5432`) |
| `POSTGRES_NAME` | DB 이름 (`codefarm`) |
| `POSTGRES_USER` | DB 사용자명 |
| `POSTGRES_PASSWORD` | DB 비밀번호 |
| **[Redis]** | |
| `REDIS_HOST` | Redis 호스트 (Docker 내부: `redis`) |
| `REDIS_PORT` | Redis 포트 (`6379`) |
| **[JWT]** | |
| `JWT_SECRET_KEY` | JWT 서명 키 (Base64) |
| `JWT_ACCESS_EXPIRATION` | Access Token 만료 (ms) |
| `JWT_REFRESH_EXPIRATION` | Refresh Token 만료 (ms) |
| **[Backend]** | |
| `SPRING_PROFILES_ACTIVE` | Spring 프로필 (`dev`/`prod`) |
| `SHOW_SQL` / `FORMAT_SQL` | SQL 로깅 설정 |
| `LOG_SQL` / `LOG_PARAM` | 로그 레벨 |
| **[외부 서비스]** | |
| `EXEC_SERVER_BASE_URL` | Execution 서버 URL |
| `FEEDBACK_SERVER_BASE_URL` | Feedback 서버 URL |
| `FEEDBACK_SERVER_TOKEN` | Feedback 인증 토큰 |
| `HINT_SERVER_BASE_URL` | AI 힌트 서버 URL |
| `HINT_SERVER_PORT` | AI 힌트 서버 포트 |
| `HINT_SERVER_TOKEN` | AI 힌트 인증 토큰 |
| **[Feedback 서비스]** | |
| `GMS_API_KEY` | GMS API 키 |
| `GMS_MODEL` | GMS 모델명 |
| `GMS_CHAT_URL` | GMS Chat API URL |
| `REQUIRE_SERVER_TOKEN` | 서버 토큰 검증 여부 |
| `REPORT_SERVER_TOKEN` | 리포트 서버 인증 토큰 |

---

## 6. 배포 시 특이사항

### 6.1 Nginx 설정

- **HTTPS**: Let's Encrypt 인증서 사용 (자동 갱신)
- **HTTP → HTTPS 리다이렉트**: 포트 80 → 443 자동 리다이렉트
- **SSE(Server-Sent Events)**: AI 힌트 기능에서 SSE 스트리밍 사용, Nginx에서 버퍼링 비활성화 설정 필요
  - `proxy_buffering off`, `proxy_cache off`, `X-Accel-Buffering no`
- **클라이언트 최대 요청 크기**: 20MB
- **타임아웃**: 3600초 (1시간) — AI 처리 시간 고려

### 6.2 Nginx 프록시 라우팅

| 경로 | 프록시 대상 | 비고 |
|------|------------|------|
| `/` | 정적 파일 (SPA) | `try_files $uri $uri/ /index.html` |
| `/api/v1/` | `http://api:8080` | 일반 REST API |
| `/api/v1/reports/feedback` | `http://feedback:8089` | 피드백 서비스 |
| `/api/v1/sessions/*/hints/subscribe` | `http://api:8080` | SSE (버퍼링 off) |
| `/execute` | `http://execution:8088` | 코드 실행 서비스 |

### 6.3 Execution 서비스 특이사항

- **Docker-in-Docker 방식**: 컨테이너 내부에서 Docker를 사용하여 코드를 격리 실행
- **Docker 소켓 마운트 필요**: `-v /var/run/docker.sock:/var/run/docker.sock`
- **동시 실행 제한**: 최대 4개 (세마포어 기반)
- **지원 언어**: Python

### 6.4 Inference (추론) 서버 환경 구축

Inference 서비스는 Docker가 아닌 **Elice GPU 컨테이너에서 직접 실행**되므로, 수동으로 환경을 구축해야 합니다.

#### 6.4.1 기본 환경 설정

```bash
# 시스템 패키지 업데이트
sudo apt update
sudo apt install net-tools tree iproute2

# 모델 저장 디렉토리 생성
cd /home/elicer/
mkdir models

# 앱 디렉토리 생성
sudo chmod 777 /srv
cd /srv
mkdir -p app/app
```

#### 6.4.2 환경 변수 파일 설정

```bash
sudo vim /srv/app/app/.env
```

`.env` 파일 내용:
```
GMS_API_KEY=<GMS API 키>
GMS_CHAT_URL=https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions
```

#### 6.4.3 GitLab Runner 설치 및 등록

```bash
# GitLab Runner 바이너리 설치
sudo curl -L --output /usr/local/bin/gitlab-runner \
  https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64
sudo chmod +x /usr/local/bin/gitlab-runner

# 서비스 사용자 생성 및 서비스 설치
sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash
sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
sudo gitlab-runner start

# Runner 등록 (프로젝트의 GitLab Runner 토큰 필요)
gitlab-runner register \
  --url https://lab.ssafy.com \
  --token <GITLAB_RUNNER_TOKEN>
```

> **참고**: Runner 등록 시 `elice-container` 태그를 지정해야 CI/CD 파이프라인에서 인식됩니다.

#### 6.4.4 Python 환경 구축 (pyenv)

```bash
# pyenv 설치
curl -fsSL https://pyenv.run | bash

# 셸 설정 (bashrc + profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init - bash)"' >> ~/.profile
exec "$SHELL"

# Python 빌드 의존성 설치
sudo apt update
sudo apt install make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev curl git \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Python 3.11.9 설치 및 가상환경 생성
pyenv install 3.11.9
pyenv global 3.11.9
pyenv virtualenv venv
pyenv activate venv
```

#### 6.4.5 ML 모델 파일 배포

모델 파일은 로컬에서 SCP로 전송합니다.

```bash
# 로컬 → Elice 서버로 모델 파일 전송
scp -i ~/.ssh/<SSH_KEY> -P <SSH_PORT> label_model.zip elicer@<ELICE_HOST>:/home/elicer/models/
scp -i ~/.ssh/<SSH_KEY> -P <SSH_PORT> text_model.zip elicer@<ELICE_HOST>:/home/elicer/models/

# 서버에서 모델 압축 해제
unzip -q /home/elicer/models/label_model.zip -d /srv/app/app/inference/models/label_model
unzip -q /home/elicer/models/text_model.zip -d /srv/app/app/inference/models/text_model
```

#### 6.4.6 모델 디렉토리 구조

```
/srv/app/app/inference/
├── app.py                    # FastAPI 메인 앱
├── requirements.txt          # Python 의존성
├── READMD.md
├── models/
│   ├── model1.py             # MODEL1 (실수 타입 분류)
│   ├── model2.py             # MODEL2 (분석 생성)
│   ├── label_model/          # 라벨 분류 모델 (safetensors)
│   │   ├── config.json
│   │   ├── model.safetensors
│   │   ├── tokenizer.json
│   │   ├── tokenizer.model
│   │   ├── tokenizer_config.json
│   │   ├── special_tokens_map.json
│   │   └── chat_template.jinja
│   └── text_model/           # 텍스트 분석 모델 (LoRA 어댑터, 5-fold)
│       ├── fold_1/
│       │   ├── adapter_config.json
│       │   ├── adapter_model.safetensors
│       │   ├── tokenizer.json
│       │   ├── tokenizer_config.json
│       │   ├── special_tokens_map.json
│       │   └── chat_template.jinja
│       ├── fold_2/ (동일 구조)
│       ├── fold_3/ (동일 구조)
│       ├── fold_4/ (동일 구조)
│       └── fold_5/ (동일 구조)
└── utils/
    ├── auth.py               # 인증 유틸
    ├── constant.py           # 상수 정의
    ├── json_utils.py         # JSON 처리
    ├── labels.py             # 라벨 정의
    ├── prompt_builder.py     # 프롬프트 빌더
    └── prompt.py             # 프롬프트 템플릿
```

#### 6.4.7 서비스 실행 (CI/CD 자동 배포)

정상 환경 구축 후에는 GitLab CI/CD의 `inference-deploy` 스테이지에서 자동 배포됩니다:

1. Git sparse checkout으로 `inference/` 디렉토리만 가져옴
2. `/srv/app/app/inference/`에 rsync
3. pyenv venv 활성화 후 `pip install -r requirements.txt`
4. 모델 zip 파일 압축 해제

#### 6.4.8 주요 특성

- **GPU 필수**: CUDA 12.8 호환 GPU
- **처리 파이프라인**: MODEL1(실수 타입 분류) → MODEL2(분석 생성) → GMS(힌트 생성)
- **동시성 제한**: GPU 워커 2개, MODEL2 워커 2개, GMS 워커 8개
- **모델 형식**: label_model(safetensors), text_model(LoRA 어댑터, 5-fold 앙상블)

### 6.5 Backend 멀티 스테이지 Docker 빌드

- **빌드 스테이지**: `gradle:9.2.1-jdk17-alpine` — JAR 생성
- **런타임 스테이지**: `eclipse-temurin:17-jre-alpine` — 경량 이미지
- **보안**: non-root 사용자(`spring`)로 실행
- **JPA DDL**: `ddl-auto: update` — 서버 시작 시 스키마 자동 업데이트

### 6.6 보안 고려사항

- Trivy FS 스캔으로 HIGH/CRITICAL 취약점 검사
- JWT 기반 인증 (Access Token + Refresh Token)
- 서비스 간 통신 시 토큰 기반 인증 (`FEEDBACK_SERVER_TOKEN`, `HINT_SERVER_TOKEN`)
- Docker 이미지에서 non-root 사용자 사용

---

## 7. DB 접속 정보 및 프로퍼티 파일 목록

### 7.1 데이터베이스 접속 정보

| 항목 | 값 |
|------|-----|
| **DBMS** | PostgreSQL **16** Alpine |
| **호스트** | 환경변수 `POSTGRES_HOST` (로컬: `localhost`, Docker: `postgres`) |
| **포트** | 환경변수 `POSTGRES_PORT` (로컬: `15432`, Docker: `5432`) |
| **데이터베이스명** | `codefarm` |
| **사용자** | 환경변수 `POSTGRES_USER` (로컬: `farmer`) |
| **비밀번호** | 환경변수 `POSTGRES_PASSWORD` |
| **JDBC URL** | `jdbc:postgresql://{HOST}:{PORT}/codefarm?connectTimeout=10&socketTimeout=10&options=-c%20TimeZone=Asia/Seoul` |
| **커넥션 풀** | HikariCP (min-idle: 5, max-pool: 10/dev:5/prod:20) |

### 7.2 Redis 접속 정보

| 항목 | 값 |
|------|-----|
| **호스트** | 환경변수 `REDIS_HOST` (로컬: `localhost`, Docker: `redis`) |
| **포트** | 환경변수 `REDIS_PORT` (로컬: `16379`, Docker: `6379`) |
| **타임아웃** | 2000ms |
| **커넥션 풀** | Lettuce (max-active: 8, max-idle: 8) |

### 7.3 주요 프로퍼티/설정 파일 목록

| 파일 경로 | 설명 |
|-----------|------|
| `backend/src/main/resources/application.yml` | 메인 설정 파일 (서버, DB, Redis, JWT, 외부 서비스 등) |
| `backend/src/main/resources/application-dev.yml` | 개발 환경 프로필 설정 |
| `backend/src/main/resources/application-prod.yml` | 프로덕션 환경 프로필 설정 |
| `backend/src/main/resources/.env` | 로컬 개발용 환경 변수 (Git 추적 대상 아님 권장) |
| `backend/build.gradle` | Gradle 빌드 설정 및 의존성 |
| `backend/settings.gradle` | Gradle 프로젝트 설정 |
| `frontend/.env.development` | 프론트엔드 개발 환경 변수 |
| `frontend/package.json` | 프론트엔드 의존성 관리 |
| `frontend/vite.config.js` | Vite 빌드/프록시 설정 |
| `frontend/tailwind.config.js` | TailwindCSS 설정 |
| `infra/nginx/conf.d/default.conf` | Nginx 설정 (프록시, SSL 등) |
| `execution/Dockerfile` | Execution 서비스 Docker 빌드 설정 |
| `feedback/Dockerfile` | Feedback 서비스 Docker 빌드 설정 |
| `feedback/requirements.txt` | Feedback 서비스 Python 의존성 |
| `inference/requirements.txt` | Inference 서비스 Python 의존성 |
| `.gitlab-ci.yml` | CI/CD 파이프라인 설정 |
| **[서버 배포 파일 — `/srv/app/`]** | |
| `/srv/app/.env` | 서버 통합 환경 변수 |
| `/srv/app/docker-compose.db.yml` | PostgreSQL + Redis 구성 |
| `/srv/app/docker-compose.dev.yml` | 개발 환경 Backend + Web |
| `/srv/app/docker-compose.prod.yml` | 프로덕션 환경 Backend + Web |
| `/srv/app/docker-compose.exec.yml` | Execution 서비스 구성 |
| `/srv/app/docker-compose.feedback.yml` | Feedback 서비스 구성 |
| `/srv/app/scripts/deploy_foundation.sh` | Foundation 배포 스크립트 |
| `/srv/app/scripts/deploy_server.sh` | Server 배포 스크립트 |
| `/srv/app/scripts/healthcheck.sh` | 헬스체크 스크립트 |
| `/srv/app/scripts/rollback.sh` | 롤백 스크립트 |

---

## 8. 외부 서비스 정보

### 8.1 Docker Hub

| 항목 | 설명 |
|------|------|
| **용도** | Docker 이미지 레지스트리 |
| **URL** | https://hub.docker.com |
| **계정** | GitLab CI/CD 변수에 `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` 등록 |
| **사용 위치** | CI/CD 파이프라인에서 이미지 빌드 & 푸시 |

### 8.2 GMS API (SSAFY 제공 AI API)

| 항목 | 설명 |
|------|------|
| **용도** | AI 피드백 생성 (Feedback 서비스), AI 힌트 생성 (Inference 서비스) |
| **API URL** | `https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions` |
| **모델** | GPT-4o-mini (환경 변수 `GMS_MODEL`로 설정) |
| **인증** | API 키 기반 (`GMS_API_KEY`) |
| **환경 변수** | `GMS_API_KEY`, `GMS_MODEL`, `GMS_CHAT_URL`, `REQUIRE_SERVER_TOKEN`, `REPORT_SERVER_TOKEN` |
| **사용 위치** | Feedback 서비스, Inference 서비스 |

### 8.3 HuggingFace

| 항목 | 설명 |
|------|------|
| **용도** | ML 모델 허브 (Transformers, 사전학습 모델) |
| **URL** | https://huggingface.co |
| **사용 위치** | Inference 서비스에서 Transformers 라이브러리를 통한 모델 로드 |

### 8.4 Let's Encrypt

| 항목 | 설명 |
|------|------|
| **용도** | SSL/TLS 인증서 발급 |
| **URL** | https://letsencrypt.org |
| **인증서 경로** | `/etc/letsencrypt/live/i14b109.p.ssafy.io/` |
| **갱신** | Certbot을 통한 자동 갱신 |

### 8.5 Elice 컨테이너 (GPU)

| 항목 | 설명 |
|------|------|
| **용도** | AI Inference 서비스 GPU 실행 환경 |
| **배포 방식** | GitLab CI/CD에서 sparse checkout 후 배포 |
| **모델 경로** | `/home/elicer/models/` |
| **앱 경로** | `/srv/app/app/inference/` |
| **Python 환경** | pyenv + virtualenv (`venv`) |

### 8.6 PyTorch (CUDA)

| 항목 | 설명 |
|------|------|
| **용도** | GPU 기반 딥러닝 추론 |
| **설치 URL** | `https://download.pytorch.org/whl/cu128` |
| **CUDA 버전** | 12.8 |

---

> **참고**: 보안 관련 값(비밀번호, 토큰, 시크릿 키 등)은 이 문서에 직접 기재하지 않으며, 해당 환경의 환경 변수 또는 시크릿 관리 시스템을 통해 별도 관리합니다.
