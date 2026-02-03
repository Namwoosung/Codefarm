# Infrastructure Overview

이 문서는 본 프로젝트의 인프라 구성과  
CI/CD, 배포 및 운영 방식에 대한 **최종 기준 문서**이다.

본 문서는 애플리케이션 비즈니스 로직이 아닌,

- GitLab CI/CD 파이프라인
- Docker 이미지 빌드 및 배포 전략
- EC2 서버 디렉토리 구조(`/srv/app`)
- Docker Compose 역할 분리 (foundation / application)
- 배포·헬스체크·롤백 스크립트 기준
- Nginx 기반 SSE(Server-Sent Events) 운영 정책

을 이해하는 것을 목표로 한다.

## 1. Current Server Directory Structure

본 프로젝트는 **단일 EC2 인스턴스**에서 모든 서비스를 운영하며,  
서버 기준 디렉토리는 `/srv/app` 이다.

```text
/srv/app
├── .env
├── .current_image_tag_dev
├── .previous_image_tag_dev
├── .current_image_tag_prod
├── .previous_image_tag_prod
├── .current_image_tag_foundation
├── .previous_image_tag_foundation
├── docker/
│   └── runner/
│       └── python/
│           └── Dockerfile
├── docker-compose.db.yml
├── docker-compose.exec.yml
├── docker-compose.feedback.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── letsencrypt-webroot/
└── scripts/
    ├── deploy_foundation.sh
    ├── deploy_server.sh
    ├── healthcheck.sh
    └── rollback.sh
````

### 1.1 Image Tag Tracking Files

* `.current_image_tag_*`, `.previous_image_tag_*`

  * 각 배포 시점의 **Docker 이미지 태그(CI_COMMIT_SHA)**를 기록
  * `rollback.sh`에서 해당 값을 참조하여 **이전 버전으로 복구**
  * 임의 삭제 시 롤백 기능이 깨질 수 있으므로 유지 필수

## 2. Deployment Layer Concept

현재 배포 구조는 **Foundation Layer**와 **Application Layer**로 분리되어 있다.

### 2.1 Foundation Layer (공통 인프라)

구성 요소:

* PostgreSQL
* Redis
* Execution Server (사용자 코드 실행)
* Feedback Server (FastAPI 기반)

사용 compose 파일:

* `docker-compose.db.yml`
* `docker-compose.exec.yml`
* `docker-compose.feedback.yml`

특징:

* 변경 빈도 낮음
* Application 배포와 독립
* 필요 시에만 **수동 배포**
* GitLab Job: `deploy-foundation`

### 2.2 Application Layer (서비스)

구성 요소:

* Backend (Spring Boot)
* Web (Vue build + Nginx serve)

환경별 compose:

* `docker-compose.dev.yml`
* `docker-compose.prod.yml`

특징:

* CI/CD를 통해 자동 배포
* develop → 자동
* main/hotfix → manual
* Foundation과 동일한 외부 네트워크(`appnet`) 사용

## 3. Networking Policy

* 모든 컨테이너는 공통 외부 네트워크 `appnet`을 사용
* 서비스 간 통신은 **컨테이너 DNS 이름 기반**

예시:

* `http://execution:8088`
* `http://feedback:8089`
* `postgres:5432`

## 4. Environment Variables Policy

### 4.1 `.env`의 역할

`/srv/app/.env`는 서버 운영에 필요한 환경변수를 보관한다.

* Docker Compose `${VAR}` 치환에 사용
* 컨테이너 런타임 환경변수 주입은

  * `env_file:` 또는
  * `environment:` 를 통해 명시적으로 수행해야 한다

예시 (Backend):

```yml
services:
  api:
    env_file:
      - .env
    environment:
      EXEC_SERVER_BASE_URL: "http://execution:8088"
```

## 5. CI/CD Pipeline Summary (`.gitlab-ci.yml`)

파이프라인 단계:

* **build**: Docker 이미지 빌드 및 Docker Hub push
* **test**: 브랜치 유형별 테스트
* **security**: Trivy 기반 정적 스캔
* **deploy**: EC2 서버 배포
* **inference**: GPU 추론 서버 배포

### 5.1 Image Tag Policy

* 모든 이미지 태그는 `CI_COMMIT_SHA` 사용
* develop / main 브랜치에서는 **항상 build 수행**

  * 배포 시 tag 불일치로 인한 pull 실패 방지

## 6. Deployment Scripts

### deploy_foundation.sh

* Foundation 레이어 배포 담당
* 대상 compose:

  * db / exec / feedback
* 태그 기록:

  * `.current_image_tag_foundation`
  * `.previous_image_tag_foundation`

### deploy_server.sh

* Application 레이어 배포 담당
* dev / prod 환경 분기
* 대상 compose:

  * `docker-compose.dev.yml`
  * `docker-compose.prod.yml`
* 태그 기록:

  * `.current_image_tag_dev|prod`
  * `.previous_image_tag_dev|prod`

### healthcheck.sh

* 환경(dev/prod/foundation)에 따라 헬스 체크 분기
* Spring Actuator 기반
* 컨테이너 restarting 상태를 고려하여

  * 타임아웃 / 재시도 정책 관리 필요

### rollback.sh

* `.previous_image_tag_*` 기준으로 롤백
* compose 재기동 방식

## 7. Nginx & SSE(Server-Sent Events) 운영 정책

### 7.1 문제 배경

배포 환경에서 **SSE 기반 스트리밍 응답이 전달되지 않는 문제**가 발생했다.

* 로컬 환경: 정상
* 배포 환경(Nginx 경유): 첫 이벤트(CONNECTED) 미수신 또는 지연

원인:

* Nginx 기본 프록시 동작

  * 응답 버퍼링
  * 캐시
  * Connection 헤더 처리
    가 SSE 특성과 맞지 않음

### 7.2 해결 전략

* SSE 엔드포인트를 **전용 location으로 분리**
* SSE에 맞게 프록시 동작 조정

적용 정책:

* `proxy_buffering off`
* `proxy_cache off`
* `proxy_request_buffering off`
* `Connection: keep-alive` 명시
* `Upgrade` 헤더 제거 (SSE는 WebSocket 아님)
* `X-Accel-Buffering: no` 헤더 추가

이로 인해:

* 첫 이벤트 즉시 전달
* 장시간 연결 유지
* 일반 REST API와 설정 충돌 방지

## 9. Minimal Rules (Team Agreement)

* 서버 운영 기준 경로는 `/srv/app`
* app 배포

  * develop: 자동
  * main/hotfix: 수동
* foundation은 필요 시에만 수동 배포
* `.env`는 서버에만 존재
* 민감 정보는 GitLab Variables로 관리
* 컨테이너 런타임 환경변수는 반드시 명시적으로 주입
* **SSE 엔드포인트는 반드시 전용 Nginx 설정을 사용한다**