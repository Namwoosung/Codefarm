# Infrastructure Overview

이 문서는 본 프로젝트의 인프라 구성과  
CI/CD, 배포 및 운영 방식에 대한 **최종 기준 문서**이다.

애플리케이션 비즈니스 로직이 아닌,

- GitLab CI/CD 파이프라인
- Docker 이미지 빌드 전략
- 서버 배포 구조
- 운영 스크립트 역할 분리

를 이해하는 것을 목표로 한다.

## Directory Structure

```bash
repo-root/
├── backend/                 # Spring Boot 애플리케이션
│   └── Dockerfile
├── frontend/                # Vue.js 애플리케이션
│   └── Dockerfile
├── infra/
│   ├── compose/             # Docker Compose 정의
│   │   ├── docker-compose.base.yml
│   │   ├── docker-compose.dev.yml
│   │   ├── docker-compose.prod.yml
│   │   ├── dev.env.example
│   │   └── prod.env.example
│   ├── nginx/               # Nginx 설정 (web 컨테이너용)
│   │   └── conf.d/
│   │       └── default.conf
│   ├── scripts/             # 배포/운영 스크립트
│   │   ├── deploy.sh
│   │   ├── healthcheck.sh
│   │   └── rollback.sh
│   └── README.md            # 인프라 문서 (본 문서)
├── .gitlab-ci.yml            # CI/CD 파이프라인 정의
└── README.md                 # 프로젝트 전반 문서
````

## Branch Strategy (Infra Perspective)

본 프로젝트는 **단순화된 Gitflow 전략**을 사용하며,
CI/CD 및 배포 자동화에 최적화되어 있다.

### Branch Roles

* **feature/***
  기능 개발 브랜치 → develop 병합

* **infra/***
  CI/CD, Docker, 배포, 서버 설정 변경 → develop 병합

* **fix/***
  개발 환경 버그 수정 → develop 병합

* **develop**
  통합 및 검증 브랜치
  → dev 환경 **자동 배포**

* **hotfix/***
  운영 환경 긴급 수정
  → main 기준 생성

* **main**
  운영(Production) 배포 전용 브랜치
  → **manual 배포**

## CI/CD Pipeline Overview

GitLab CI/CD를 사용하며,
**빌드와 배포를 명확히 분리**한다.

### Pipeline Stages

1. **build**

   * backend / frontend Docker 이미지 빌드
   * Docker Hub로 push
   * 태그 전략: `CI_COMMIT_SHA`

2. **test**

   * feature / infra / fix → fast test
   * develop / main / hotfix → full test

3. **deploy**

   * 서버에서는 **이미지 pull + compose up만 수행**
   * 소스 코드 git pull ❌

## Deployment Strategy

### 핵심 원칙

* ✅ **CI에서 Docker 이미지를 빌드**
* ✅ **서버는 실행 환경만 담당**
* ❌ 서버에서 git pull / build 하지 않음

---

### Dev Environment

* 대상 브랜치: `develop`
* 배포 방식: **자동 배포**
* 서버 경로: `/srv/app-dev`
* 동작 방식:

  1. CI에서 이미지 빌드 & push
  2. SSH로 dev 서버 접속
  3. `deploy.sh dev` 실행
  4. `docker compose pull && up -d`

### Prod Environment

* 대상 브랜치: `main`, `hotfix/*`
* 배포 방식: **manual trigger**
* 서버 경로: `/srv/app-prod`
* 동작 방식:

  1. CI에서 이미지 빌드 & push
  2. 승인 후 배포 실행
  3. `deploy.sh prod`

## Docker Compose Strategy

Compose 파일은 **역할별로 분리**한다.

### docker-compose.base.yml

* 공통 서비스 정의

  * backend(api)
  * frontend(web)
  * postgres
  * redis
* image, network, volume, healthcheck 정의
* **단독 실행 불가**

### docker-compose.dev.yml / prod.yml

* 환경별 override 전용
* ports, container_name 등 환경 차이만 정의
* 반드시 base와 함께 사용

```bash
docker compose \
  -f docker-compose.base.yml \
  -f docker-compose.dev.yml \
  --env-file dev.env \
  up -d
```

---

## Environment Variables

* 실제 값은 **서버에만 존재**
* 레포에는 `.env.example`만 관리

### dev.env / prod.env 포함 항목

* Spring profile
* DB / Redis 접속 정보
* Docker Hub 사용자명

❌ `IMAGE_TAG`는 env 파일에 넣지 않음
→ CI에서 주입

## Deployment Scripts

모든 배포 로직은 **서버의 스크립트**에서 수행한다.

### deploy.sh

* dev / prod 공통 배포 스크립트
* base + env compose 병합 실행
* 현재/이전 이미지 태그 기록

### healthcheck.sh

* compose 상태 확인
* backend actuator 기반 health check
* base + env compose를 반드시 함께 사용

### rollback.sh

* `.previous_image_tag` 기준 롤백
* 이미지 pull 후 compose 재기동
* 태그 스왑 방식으로 연속 롤백 지원

## Security & Operations

* 민감 정보는 GitLab CI/CD Variables로 관리
* prod 관련 변수는 **Protected** 적용
* 서버 접근은 SSH key 기반
* main 브랜치 direct push 금지

## Operational Notes

* 서버 초기 세팅 시 디렉토리 생성

```bash
mkdir -p /srv/app-dev /srv/app-prod
chmod +x /srv/app-*/infra/scripts/*.sh
```

* 문제 발생 시 점검 순서

  1. GitLab CI 로그
  2. deploy / healthcheck 로그
  3. docker ps / docker logs