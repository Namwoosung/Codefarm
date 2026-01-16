# Jenkins CI/CD 구축 정리

## 목차
1. [개요](#개요)
2. [Jenkins 설치](#jenkins-설치)
3. [CI/CD 구축](#cicd-구축)
4. [프론트 배포](#프론트-배포)
5. [Gateway 분리](#gateway-분리)

---

## 개요

### 개념

**Jenkins**: 빌드/테스트/배포 작업을 자동으로 실행해주는 서버(자동화 도구)

자동화되는 과정:
- 코드 수정 → Git push
- 서버(EC2) 접속
- 최신 코드 pull
- Spring Boot 빌드(Gradle)
- Docker 이미지 빌드
- docker-compose 재시작
- 로그 확인

### CI/CD

**CI (Continuous Integration)**: 지속적 통합
- 여러 사람의 작업 시 코드 통합 시 자동 검증
- `develop` 브랜치에 push 시 자동으로:
  - 코드 받기
  - 빌드
  - 테스트
  - 정적 분석(선택)
  - 결과 알림(성공/실패)

> CI는 배포와 무관하게, 통합이 안전한지 빌드/테스트가 통과하는지 확인하는 과정

**CD (Continuous Delivery / Continuous Deployment)**
1. **Continuous Delivery**: 배포 가능 상태까지 자동화, 실제 배포는 수동 승인
2. **Continuous Deployment**: 배포까지 완전 자동화

### Jenkins 기본 동작

1. **언제 실행할지 결정 (Trigger)**
   - push, PR, 스케줄, 태그 등
2. **뭘 실행할지 정의 (Pipeline)**
   - 빌드, 테스트, Docker 이미지 생성, 배포
3. **결과 기록 및 공유 (Report)**
   - 성공/실패 로그, 실패 지점, 원인

**Pipeline**: 자동화 절차를 단계별로 정의한 레시피
- Checkout → Build → Test → Package → Deploy

| Jenkins 요소 | 설명 |
| --- | --- |
| Controller | 두뇌 역할, 웹 UI 제공, Job/Pipeline 관리 |
| Agent | 실제 작업 수행 (빌드, 테스트, 배포) |
| Pipeline | 업무 지시서 |
| Jenkinsfile | 업무 매뉴얼 (코드로 정의) |

### 기본 구조

**역할**
1. **Jenkins Controller**: 두뇌 역할
   - 웹 UI 제공
   - Job/Pipeline 관리
   - Jenkinsfile 해석
2. **Jenkins Agent**: 실제 작업 수행

**구성 방식**

**단일 노드 Jenkins** (초보자 & 개인 프로젝트)
- Controller = Agent = 같은 서버
- 설정 단순, 소규모 서비스에 적합
- Jenkins 장애 시 배포 불가, 부하 분산 불가

**멀티 노드 Jenkins** (실무 / 대규모)
- Controller 전용 서버 + Agent 여러 대
- 확장성 좋음, 보안/권한 분리 가능
- 설정 난이도 상승

**설치 방식**
1. EC2에 직접 설치
2. Docker 컨테이너 (권장)
3. Managed CI (GitHub Actions 등)

**Docker 컨테이너로 실행 시 구조**
```
[EC2]
 ├─ Docker
 ├─ Jenkins 컨테이너
 │    └─ /var/jenkins_home (볼륨)
 ├─ docker.sock (마운트)
 └─ 서비스 컨테이너들
```

- `/var/jenkins_home` 볼륨: Jenkins 데이터 영속화 필수
- `docker.sock` 마운트: Jenkins가 호스트 Docker 제어

### 플러그인

Jenkins는 기본적으로 제한된 기능만 제공. 외부 도구 연동은 플러그인 필요.

**핵심 플러그인**
1. Pipeline 관련 (필수)
2. SCM / Git 연동
3. Credentials / 보안
4. 빌드/배포 도구 연동 (Docker, SSH, AWS)
5. UI / 편의성

> ⚠️ 플러그인 함부로 업데이트 금지! 버전 고정 → 필요시만 업데이트 → 백업 후 테스트

### Jenkins Job

**Job 분류**
- **Freestyle Job**: UI 기반, 단순 (개인 실험용)
- **Pipeline Job**: Jenkinsfile 기반, 코드로 관리 (실무 표준)
- **Multibranch Pipeline**: 브랜치 자동 관리 (실무에서 가장 많이 사용)

**Pipeline Job 특징**
- Git 기반 관리
- 재현 가능
- 리뷰 가능
- 팀 협업에 최적

### Jenkinsfile 문법

**Jenkinsfile**: CI/CD 파이프라인을 정의한 코드 파일
- Git 저장소에 함께 관리
- 프로젝트 root에 위치

**문법 스타일**
1. **Declarative Pipeline** (권장, 표준)
2. **Scripted Pipeline** (고급, 자유도 높음)

**기본 구조**
```groovy
pipeline {
  agent any

  environment {
    // 환경 변수
  }

  stages {
    stage('Checkout') {}
    stage('Build') {}
    stage('Test') {}
    stage('Deploy') {}
  }

  post {
    success {}
    failure {}
    always {
      cleanWs()  // 필수: 디스크 공간 확보
    }
  }
}
```

**주요 요소**
- `agent`: 실행할 머신 지정 (`agent any` = 아무 Agent에서 실행)
- `stages` / `stage`: 파이프라인 단계 정의
- `steps`: 실제 실행 명령
- `environment`: 환경 변수 관리
- `post`: 파이프라인 종료 후 처리
- `when`: 조건 분기 (브랜치별 동작)

### Git 연동

**방식**
1. **Poll SCM**: Jenkins가 주기적으로 Git 확인 (비효율적)
2. **Webhook**: Git이 Jenkins 호출 (표준)

**Webhook 설정**
- Jenkins URL: `http://<JENKINS_IP>:8080/github-webhook/`
- GitHub → Settings → Webhooks
- Events: Push, Pull request

**브랜치별 동작 예시**
```groovy
develop → CI만
main    → CI + CD
```

### Credentials

**보안 정보 관리**
- GitHub 토큰
- EC2 SSH 키
- AWS Access Key / Secret Key
- DB 비밀번호
- Docker Hub 토큰

**Credentials 특징**
- Jenkins 내부에 암호화 저장
- Jenkinsfile에 직접 값 노출 안 됨
- ID로만 참조

**Credential 종류**
1. Secret Text (가장 많이 사용)
2. Username with Password
3. SSH Username with private key
4. AWS Credentials

### 무중단 배포

**단순 배포 문제점**
- 컨테이너가 내려가는 순간 요청 100% 실패
- 배포 시간 = 서비스 중단 시간

**무중단 배포 전략**

| 전략 | 난이도 | 운영 안정성 |
| --- | --- | --- |
| 단순 재시작 | ⭐ | ❌ |
| Rolling Update | ⭐⭐ | ⭕ |
| Blue/Green | ⭐⭐⭐ | ⭐⭐⭐ |
| Canary | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Blue/Green 배포**
- Blue = 현재 운영 중
- Green = 새 버전
- 트래픽을 한 번에 전환
- 무중단 보장, 롤백 쉬움
- 컨테이너 2세트 필요

---

## Jenkins 설치

### Docker 설치 (Ubuntu 22.04)

```bash
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg

# Docker 공식 GPG 키 등록
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Docker repo 등록
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker

# 현재 유저가 docker 명령 사용 가능하도록 설정
sudo usermod -aG docker $USER
```

### Jenkins 실행

**1. Jenkins 데이터 디렉토리 생성**
```bash
sudo mkdir -p /var/jenkins_home
sudo chown -R 1000:1000 /var/jenkins_home
```

> Jenkins 컨테이너 내부 기본 유저(uid=1000)가 이 디렉토리를 사용해야 하므로 권한 설정 중요

**2. Jenkins용 Dockerfile 생성**

```dockerfile
FROM jenkins/jenkins:lts

USER root

# docker CLI 설치
RUN apt-get update \
 && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

RUN curl -fsSL https://get.docker.com | sh

# docker-compose v2 (plugin 방식)
RUN mkdir -p /usr/libexec/docker/cli-plugins \
 && curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 \
    -o /usr/libexec/docker/cli-plugins/docker-compose \
 && chmod +x /usr/libexec/docker/cli-plugins/docker-compose

USER jenkins
```

**3. 이미지 빌드 및 컨테이너 실행**

```bash
# 이미지 빌드
docker build -t jenkins-with-docker .

# 컨테이너 실행
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v /var/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --group-add $(getent group docker | cut -d: -f3) \
  --restart unless-stopped \
  jenkins-with-docker
```

**옵션 설명**
- `-v /var/jenkins_home:/var/jenkins_home`: Jenkins 데이터 영속화
- `-v /var/run/docker.sock:/var/run/docker.sock`: 호스트 Docker 제어
- `--group-add`: docker.sock 접근 권한 부여

**4. 초기 설정**
- 브라우저에서 `http://<EC2_IP>:8080` 접속
- 초기 비밀번호 확인:
  ```bash
  docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  ```
- 추천 플러그인 설치
- 관리자 계정 생성

**5. Docker 제어 확인**
```bash
docker exec -it jenkins bash
docker version
docker ps
exit
```

**Jenkins 운영 기본 설정**
1. Jenkins 포트는 내 IP만 허용 (Security Group)
2. 플러그인 업데이트 함부로 하지 않기
3. `/var/jenkins_home` 백업
4. 디스크 모니터링 (workspace/log 정리)
5. 시간/타임존 확인

---

## CI/CD 구축

### 초기 세팅

**배포용 디렉토리 생성**
```bash
sudo mkdir -p /opt/app
sudo chown -R $USER:$USER /opt/app
cd /opt/app
```

**docker-compose.yml 생성**
```yaml
version: "3.8"

services:
  redis:
    image: redis:alpine
    container_name: app-redis
    ports:
      - "6379:6379"
    restart: unless-stopped

  backend:
    image: ${BACKEND_IMAGE}
    container_name: app-backend
    ports:
      - "8080:8080"
    env_file:
      - .env.prod
    depends_on:
      - redis
    restart: on-failure
```

**환경 변수 파일 생성**
```bash
vi /opt/app/.env.prod
chmod 600 /opt/app/.env.prod
```

### Jenkins 설치 및 기본 구성

**Jenkins 분리 구성 (권장)**
- Jenkins 전용 EC2 생성
- 운영 서버와 분리하여 보안 강화

**Jenkins EC2 설정**
1. Docker 설치
2. Jenkins 데이터 볼륨 준비
3. Jenkins Dockerfile 생성 및 이미지 빌드
4. Jenkins 컨테이너 실행
5. 초기 설정 및 플러그인 설치

**Credentials 설정**
1. **Docker Hub Credential**
   - Docker Hub → Personal Access Tokens 생성
   - Jenkins에 Username/Password 타입으로 등록

2. **EC2 SSH Credential**
   - Jenkins EC2에서 SSH 키 생성
   - App EC2에 public key 등록
   - Jenkins에 SSH Username with private key 타입으로 등록

### CI/CD 구성

**배포 스크립트 생성**

```bash
vi /opt/app/scripts/deploy.sh
```

```bash
#!/usr/bin/env bash
set -euo pipefail

DEPLOY_DIR="/opt/app"
COMPOSE_FILE="docker-compose.prod.yml"

: "${BACKEND_IMAGE:?BACKEND_IMAGE is required}"
: "${DOCKERHUB_REPO:?DOCKERHUB_REPO is required}"

echo "[1/6] Move to deploy dir: ${DEPLOY_DIR}"
cd "${DEPLOY_DIR}"

echo "[2/6] Docker login"
if [[ -n "${DOCKER_USER:-}" && -n "${DOCKER_PASS:-}" ]]; then
  echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
else
  echo "DOCKER_USER/DOCKER_PASS not provided. Assuming already logged in."
fi

echo "[3/6] Pull image: ${BACKEND_IMAGE}"
BACKEND_IMAGE="${BACKEND_IMAGE}" docker compose -f "${COMPOSE_FILE}" pull

echo "[4/6] Apply compose up (replace container)"
BACKEND_IMAGE="${BACKEND_IMAGE}" docker compose -f "${COMPOSE_FILE}" up -d

echo "[5/6] Show status"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "[6/6] Done."
```

```bash
chmod +x /opt/app/scripts/deploy.sh
```

**Jenkinsfile 작성**

```groovy
pipeline {
  agent any

  environment {
    DOCKERHUB_REPO = "your-username/your-backend"
    IMAGE_TAG      = "${BUILD_NUMBER}"
    APP_HOST       = "ubuntu@<PRIVATE_IP>"
    DEPLOY_SCRIPT  = "/opt/app/scripts/deploy.sh"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Image') {
      steps {
        sh """
          docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} .
          docker tag ${DOCKERHUB_REPO}:${IMAGE_TAG} ${DOCKERHUB_REPO}:latest
        """
      }
    }

    stage('Docker Login & Push') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-cred',
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          sh """
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}
            docker push ${DOCKERHUB_REPO}:latest
          """
        }
      }
    }

    stage('Deploy to App EC2') {
      steps {
        sshagent(credentials: ['app-ec2-ssh']) {
          withCredentials([usernamePassword(
            credentialsId: 'dockerhub-cred',
            usernameVariable: 'DOCKER_USER',
            passwordVariable: 'DOCKER_PASS'
          )]) {
            sh """
              ssh -o StrictHostKeyChecking=no ${APP_HOST} '
                export DOCKERHUB_REPO=${DOCKERHUB_REPO}
                export BACKEND_IMAGE=${DOCKERHUB_REPO}:${IMAGE_TAG}
                export DOCKER_USER=${DOCKER_USER}
                export DOCKER_PASS=${DOCKER_PASS}
                bash ${DEPLOY_SCRIPT}
              '
            """
          }
        }
      }
    }
  }

  post {
    always {
      cleanWs()
    }
  }
}
```

**Jenkins Pipeline Job 생성**
1. New Item → Pipeline
2. Build History: 최대 20개 유지
3. Do not allow concurrent builds: 동시 실행 방지
4. Trigger: GitHub hook trigger for GITScm polling
5. Pipeline: Pipeline script from SCM
   - SCM: Git
   - Repository URL: GitHub 레포 주소
   - Script Path: Jenkinsfile
   - Branch: main

**GitHub Webhook 설정**
- GitHub Repo → Settings → Webhooks
- Payload URL: `http://<JENKINS_IP>:8080/github-webhook/`
- Content type: `application/json`
- Events: Push, Pull request

**Jenkins 튜닝 (t3.micro)**
- Swap 메모리 추가 (2GB)
  ```bash
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  ```
- EC2 볼륨 증가 후 확장
  ```bash
  sudo growpart /dev/nvme0n1 1
  sudo resize2fs /dev/nvme0n1p1
  ```

---

## 프론트 배포

### Vercel 배포

1. Vercel → Add New Project → GitHub 연동
2. 프로젝트 설정 후 Deploy
3. `vercel.json` 추가 (SPA 라우팅)
   ```json
   {
     "rewrites": [
       {
         "source": "/(.*)",
         "destination": "/index.html"
       }
     ]
   }
   ```

### 도메인 연동

1. 도메인 구매 (예: 가비아)
2. DNS 레코드 설정
   - CNAME: 도메인을 다른 도메인으로 연결
   - A: 도메인을 IP로 연결
3. Vercel DNS 값 입력
4. Vercel에서 validate 확인

### 백엔드 HTTPS 설정

**문제**: 프론트는 HTTPS인데 백엔드는 HTTP → 브라우저 차단

**해결**: Nginx를 통한 HTTPS 제공

**Nginx 역할**
- HTTPS(443) 요청 받기
- 인증서 관리 (Let's Encrypt)
- 자동 갱신
- 내부로는 HTTP로 Spring Boot에 전달

**구조**
```
브라우저
https://api.example.com
        ↓ (HTTPS)
     Nginx
        ↓ (HTTP, 내부)
Spring Boot :8080
```

**Nginx 추가 (docker-compose)**

```yaml
version: "3.8"

services:
  redis:
    image: redis:alpine
    container_name: app-redis
    ports:
      - "6379:6379"
    restart: unless-stopped

  backend:
    image: ${BACKEND_IMAGE:-your-username/your-backend:latest}
    container_name: app-backend
    expose:
      - "8080"
    env_file:
      - /opt/app/.env.prod
    depends_on:
      - redis
    restart: on-failure

  nginx:
    image: nginx:1.25-alpine
    container_name: app-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /opt/app/nginx/conf.d:/etc/nginx/conf.d
      - /opt/app/nginx/certbot/conf:/etc/letsencrypt
      - /opt/app/nginx/certbot/www:/var/www/certbot
    depends_on:
      - backend
    restart: unless-stopped

  certbot:
    image: certbot/certbot:latest
    container_name: app-certbot
    volumes:
      - /opt/app/nginx/certbot/conf:/etc/letsencrypt
      - /opt/app/nginx/certbot/www:/var/www/certbot
    entrypoint: /bin/sh
    command: -c "sleep infinity"
    restart: unless-stopped
```

**Nginx 설정 (HTTP 먼저)**

```nginx
server {
    listen 80 default_server;
    server_name api.example.com _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://backend:8080;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Let's Encrypt 인증서 발급**

```bash
docker exec -it app-certbot certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d api.example.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

**Nginx HTTPS 설정**

```nginx
# 80: HTTPS로 리다이렉트 (certbot 예외 허용)
server {
    listen 80;
    server_name api.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://api.example.com$request_uri;
    }
}

# 80: 나머지는 버림
server {
    listen 80 default_server;
    server_name _;
    return 444;
}

# 443: 실제 API
server {
    listen 443 ssl;
    http2 on;
    server_name api.example.com;

    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;

    proxy_connect_timeout 5s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    send_timeout 60s;

    location / {
        proxy_pass http://backend:8080;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        proxy_buffering off;
    }
}
```

**인증서 자동 갱신 (Cron)**

```bash
crontab -e
# 아래 한 줄 추가
0 3 * * * docker exec app-certbot certbot renew --quiet && docker exec app-nginx nginx -s reload
```

---

## Gateway 분리

### Gateway EC2 구축

**목적**
- Reverse Proxy 역할
- Load Balancing
- 무중단 배포
- 라우팅
- HTTPS 분리

**구조**
```
브라우저
https://api.example.com
        ↓
   Gateway EC2 (Nginx)
        ↓ (Private IP)
   App EC2 (Spring Boot)
```

**Gateway EC2 설정**
1. Security Group 생성 (80, 443 포트 오픈)
2. EC2 생성
3. EIP 할당
4. Swap 메모리 확보
5. Docker 설치
6. Nginx 구성

**docker-compose.yml**

```yaml
version: "3.8"

services:
  nginx:
    image: nginx:1.25-alpine
    container_name: gateway-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /opt/gateway/nginx/conf.d:/etc/nginx/conf.d
      - /opt/gateway/nginx/certbot/conf:/etc/letsencrypt
      - /opt/gateway/nginx/certbot/www:/var/www/certbot
      - /opt/gateway/logs:/var/log/nginx
    restart: unless-stopped

  certbot:
    image: certbot/certbot:latest
    container_name: gateway-certbot
    volumes:
      - /opt/gateway/nginx/certbot/conf:/etc/letsencrypt
      - /opt/gateway/nginx/certbot/www:/var/www/certbot
    entrypoint: /bin/sh
    command: -c "sleep infinity"
    restart: unless-stopped
```

**Nginx 설정 (Upstream 사용)**

```nginx
upstream backend_upstream {
    server <PRIVATE_IP>:8080;
    keepalive 32;
}

# 80 -> 443 리다이렉트
server {
    listen 80;
    server_name api.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://api.example.com$request_uri;
    }
}

server {
    listen 80 default_server;
    server_name _;
    return 444;
}

# HTTPS
server {
    listen 443 ssl;
    http2 on;
    server_name api.example.com;

    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_pass http://backend_upstream;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        proxy_connect_timeout 3s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
}
```

**App EC2 정리**
1. Security Group: 8080 포트는 Gateway만 접근 가능하도록 설정
2. Nginx/Certbot 제거
3. docker-compose.yml 수정 (backend만 expose)

---

## 무중단 배포 설계

**고려사항**
- Blue/Green 배포 전략
- Nginx upstream 다중 서버 구성
- 헬스 체크
- 롤백 전략

**향후 개선 방향**
- 무중단 배포 자동화
- 모니터링 및 알림
- 로그 수집 및 분석
