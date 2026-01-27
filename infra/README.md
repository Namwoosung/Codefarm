# Infrastructure Overview

이 문서는 본 프로젝트의 인프라 구성과
CI/CD, 배포 및 운영 방식에 대한 **최종 기준 문서**입니다.

본 문서는 애플리케이션 비즈니스 로직이 아닌,

* GitLab CI/CD 파이프라인
* Docker 이미지 빌드 및 배포 전략
* EC2 서버 디렉토리 구조
* 배포 스크립트 및 Docker Compose 역할 분리

를 이해하는 것을 목표로 합니다.

## 1. Current Server Directory Structure

본 프로젝트는 **단일 EC2 인스턴스**에서 모든 환경을 운영하며,
서버 내 기준 디렉토리는 `/srv/app` 입니다.

```text
/srv/app
├── .env
├── .current_image_tag_dev
├── .previous_image_tag_dev
├── docker/
│   └── runner/
│       └── python/
│           └── Dockerfile
├── docker-compose.db.yml
├── docker-compose.exec.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
└── scripts/
    ├── deploy_foundation.sh
    ├── deploy_server.sh
    ├── healthcheck.sh
    └── rollback.sh
```

> 기존 `/srv/app-dev`, `/srv/app-prod` 구조는 **폐기 예정**이며
> 현재는 단일 경로(`/srv/app`) 기준으로 통합 관리합니다.

## 2. Background & Cleanup Rationale

기존 레포지토리에는 다음과 같은 Docker Compose 파일들이 존재했습니다.

* `docker-compose.base.yml`
* `docker-compose.dev.yml`
* `docker-compose.prod.yml`

이 파일들은 과거 구조에서 사용되었으나,

* 서버 구조 변경
* CI/CD 기반 이미지 배포 방식 도입
* foundation / application 레이어 분리

이후 **더 이상 실제 배포 및 운영에 사용되지 않게 되었습니다.**

이번 정리 작업에서는

> **실제 서버에서 사용 중인 compose 파일만을 기준으로 레포지토리를 정리**
> 하여, 혼란을 줄이고 운영 기준을 명확히 하는 것을 목표로 했습니다.

## 3. Deployment Layer Concept

현재 배포 구조는 **두 개의 레이어로 분리**되어 있습니다.

### 3.1 Foundation Layer (공통 인프라)

* DB (PostgreSQL)
* Redis
* Execution Server (사용자 코드 실행)

**사용 compose 파일**

* `docker-compose.db.yml`
* `docker-compose.exec.yml`

**특징**

* 자주 변경되지 않음
* application 배포와 독립
* manual 배포

```bash
docker compose -p foundation -f docker-compose.db.yml --env-file .env up -d
docker compose -p foundation -f docker-compose.exec.yml --env-file .env up -d
```

### 3.2 Application Layer (서비스)

* Backend (Spring Boot)
* Frontend (Nginx + Web)

**환경별 compose 파일**

* `docker-compose.dev.yml`
* `docker-compose.prod.yml`

**특징**

* CI/CD를 통해 이미지 자동 갱신
* 환경별로 분리된 compose 유지
* foundation 네트워크(appnet)에 연결

## 4. CI/CD & Branch Strategy (Infra Perspective)

### Branch Roles

* **feature/***
  기능 개발 → `develop` 병합

* **infra/***
  Docker, CI/CD, 서버 구조 변경 → `develop` 병합

* **fix/***
  개발 환경 버그 수정 → `develop` 병합

* **develop**

  * dev 환경 자동 배포
  * `docker-compose.dev.yml` 사용

* **main / hotfix/**

  * prod 환경 배포
  * manual trigger
  * `docker-compose.prod.yml` 사용

## 5. Deployment Scripts

### deploy_foundation.sh

* foundation layer 전용 배포
* db / exec compose 실행

### deploy_server.sh

* dev / prod 공통
* application layer 배포
* 이미지 태그 기록:

  * `.current_image_tag_dev`
  * `.previous_image_tag_dev`

### healthcheck.sh

* foundation / dev / prod 모드 분기
* backend actuator 기반 헬스 체크

### rollback.sh

* 이전 이미지 태그 기준 롤백
* compose 재기동 방식

## 6. Environment Variables

* `.env` 파일은 **서버에만 존재**
* GitLab CI/CD Variables로 관리

포함 항목:

* Spring profile
* DB / Redis 접속 정보
* Docker Hub 인증 정보

❌ `IMAGE_TAG`는 `.env`에 정의하지 않음
→ CI에서 주입

## 7. Operational Notes

### 서버 초기 세팅

```bash
mkdir -p /srv/app
chmod +x /srv/app/scripts/*.sh
```

### 문제 발생 시 점검 순서

1. GitLab CI 로그
2. deploy / healthcheck 로그
3. `docker ps`, `docker logs`

## 8. Why Old Compose Files Were Removed

* 실제 서버에서 **사용되지 않음**
* 현재 배포 흐름과 불일치
* 신규 인원 온보딩 시 혼란 가능성

👉 따라서 **실제 운영 기준과 맞지 않는 compose 파일은 제거**했습니다.