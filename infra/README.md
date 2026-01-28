# Infrastructure Overview

이 문서는 본 프로젝트의 인프라 구성과  
CI/CD, 배포 및 운영 방식에 대한 **최종 기준 문서**입니다.

본 문서는 애플리케이션 비즈니스 로직이 아닌,

- GitLab CI/CD 파이프라인
- Docker 이미지 빌드 및 배포 전략
- EC2 서버 디렉토리 구조(`/srv/app`)
- Docker Compose 역할 분리(db/exec/feedback/app)
- 배포/헬스체크/롤백 스크립트 기준

을 이해하는 것을 목표로 합니다.

## 1. Current Server Directory Structure

본 프로젝트는 **단일 EC2 인스턴스**에서 모든 서비스를 운영하며,  
서버 기준 디렉토리는 `/srv/app` 입니다.

```text
/srv/app
├── .env
├── .current_image_tag_dev
├── .previous_image_tag_dev
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
└── scripts/
    ├── deploy_foundation.sh
    ├── deploy_server.sh
    ├── healthcheck.sh
    └── rollback.sh
````

* `.current_image_tag_*`, `.previous_image_tag_*`

  * **배포 시점의 이미지 태그(커밋 SHA)를 기록**하기 위한 파일입니다.
  * `rollback.sh`에서 이 값을 사용해 **이전 버전으로 복구**합니다.
  * 임의 삭제 시 롤백 기능이 깨질 수 있으므로 유지 권장.

## 2. Deployment Layer Concept (Foundation vs Application)

현재 배포 구조는 **두 레이어로 분리**되어 있습니다.

### 2.1 Foundation Layer (공통 인프라)

* PostgreSQL
* Redis
* Execution Server (사용자 제출 코드 실행 서버)
* Feedback Server (FastAPI + Python)

**사용 compose 파일**

* `docker-compose.db.yml`
* `docker-compose.exec.yml`
* `docker-compose.feedback.yml`

**특징**

* 자주 변경되지 않음
* application 배포와 독립
* 필요 시 **manual 배포**(GitLab job `deploy-foundation`)

### 2.2 Application Layer (서비스)

* Backend (Spring Boot)
* Web (Vue build + Nginx serve)

**환경별 compose 파일**

* `docker-compose.dev.yml`
* `docker-compose.prod.yml`

**특징**

* CI/CD를 통해 이미지 자동 갱신
* 환경별 compose 유지
* Foundation이 사용하는 외부 네트워크(`appnet`)에 연결

## 3. Networking Policy

* 모든 컨테이너는 공통 외부 네트워크 `appnet`을 사용합니다.
* 서비스 간 통신은 **컨테이너 DNS 이름**으로 합니다.

  * 예: `http://execution:8088`, `http://feedback:8089`, `postgres:5432`

## 4. Environment Variables Policy

### 4.1 `.env`의 역할

`/srv/app/.env`는 서버 운영에 필요한 환경변수를 보관합니다.

* Compose 파일 내 `${VAR}` 치환에 사용
* 또한 **컨테이너 런타임 환경변수 주입에는 `env_file:` 또는 `environment:` 설정이 필요**합니다.



예시 (backend/api 서비스):

```yml
services:
  api:
    env_file:
      - .env
    environment:
      # 필요 시 추가 오버라이드 가능
      EXEC_SERVER_BASE_URL: "http://execution:8088"
```

### 4.2 필수 환경변수 예시

* DB/Redis 연결
* JWT, Spring profile
* 외부 서비스 base url 등

특히 아래 값은 backend 구동에 필수일 수 있습니다:

* `EXEC_SERVER_BASE_URL=http://execution:8088`
* (필요 시) `FEEDBACK_SERVER_BASE_URL=http://feedback:8089`

## 5. CI/CD Pipeline Summary (`.gitlab-ci.yml`)

파이프라인 단계:

* **build**: 이미지 빌드 + Docker Hub push
* **test**: 브랜치 유형별 테스트(현재는 echo placeholder)
* **deploy**: EC2에서 pull + compose up

### 5.1 Build Jobs

* `build-backend` → `backend/Dockerfile`
* `build-web` → `infra/nginx/Dockerfile` (멀티스테이지로 dist 빌드 + nginx serve)
* `build-execution` → `execution/Dockerfile`
* `build-feedback` → `feedback/Dockerfile`

태그 정책:

* `IMAGE_TAG = CI_COMMIT_SHA`

빌드/푸시 대상 브랜치:

* `develop`, `main`, `hotfix/*`

### 5.2 Deploy Jobs

* `deploy-dev`

  * develop push 시 자동 실행
  * `/srv/app/scripts/deploy_server.sh dev`

* `deploy-prod`

  * main/hotfix 에서 **manual**
  * `/srv/app/scripts/deploy_server.sh prod`

* `deploy-foundation`

  * develop/main/hotfix 에서 **manual**
  * `/srv/app/scripts/deploy_foundation.sh`
  * Execution/Feedback + DB/Redis 운영 레이어 담당

## 6. Deployment Scripts

### deploy_foundation.sh

* foundation 레이어 배포 담당
* 대상 compose:

  * `docker-compose.db.yml`
  * `docker-compose.exec.yml`
  * `docker-compose.feedback.yml`
* 태그 기록:

  * `.current_image_tag_foundation`
  * `.previous_image_tag_foundation`

### deploy_server.sh

* dev/prod 서비스 배포 담당
* 대상 compose:

  * `docker-compose.dev.yml` 또는 `docker-compose.prod.yml`
* 태그 기록:

  * `.current_image_tag_dev|prod`
  * `.previous_image_tag_dev|prod` (환경에 맞게)

### healthcheck.sh

* dev/prod/foundation 모드 분기
* backend actuator 기반으로 헬스 체크
* 컨테이너가 restarting 상태면 `exec`가 실패할 수 있으므로

  * **healthcheck 타임아웃/재시도 정책**을 함께 관리 권장

### rollback.sh

* `.previous_image_tag_*` 기준으로 롤백
* compose 재기동 방식

## 7. Operational Notes / Troubleshooting

### 7.1 배포 실패(컨테이너 이름 충돌) 대응

에러 예:

* `Conflict. The container name "/redis" is already in use ...`

원인:

* `container_name: redis` 같이 고정 이름을 쓰는 경우
* 기존 컨테이너가 남아있으면 compose가 새 컨테이너를 만들 수 없음

대응:

* 가능하면 `container_name` 제거 권장
* 급한 경우 기존 컨테이너만 제거(볼륨은 유지):

```bash
docker rm -f redis
```

> ✅ DB 데이터가 날아가는지는 **컨테이너 삭제 여부가 아니라 볼륨 삭제 여부**에 달려 있습니다.
>
> * `docker rm -f postgres` → 데이터 유지(볼륨 유지 시)
> * `docker volume rm ...` 또는 `docker compose down -v` → 데이터 삭제

### 7.2 Backend가 restarting 반복되는 경우

1. `docker logs --tail=200 api-dev`로 원인 확인
2. 대표 원인:

* 환경변수 누락 (`Could not resolve placeholder ...`)
* DB 스키마 변경 충돌(DDL 실패)
* 외부 서버 주소 잘못됨 (execution/feedback base url)

3. 환경변수 누락 시 조치:

* `.env`에 변수 추가
* `docker-compose.*.yml`의 해당 서비스에 `env_file: [.env]` 또는 `environment:`로 주입

검증:

```bash
docker exec -it api-dev printenv | grep EXEC_SERVER_BASE_URL
```

## 8. Why Compose Files Are Split

초기에는 단일 compose에 모든 서비스가 몰리면서,

* 변경 잦은 app 레이어와
* 거의 고정인 foundation 레이어가
  서로 배포에 영향을 주는 문제가 있었습니다.

현재 구조는 다음 장점이 있습니다:

* foundation 변경 없이 app만 빠르게 재배포 가능
* 장애 시 롤백 단위가 명확
* 신규 온보딩 시 “어디를 만져야 하는지” 명확

## 9. Minimal Rules (Team Agreement)

* 서버 운영 기준 경로는 `/srv/app`
* app 배포는 develop 자동, main/hotfix 수동
* foundation은 필요 시에만 수동 배포
* `.env`는 서버에만 존재하며, 민감정보는 GitLab Variables로 관리
* 컨테이너 런타임 환경변수는 `env_file` 또는 `environment`로 명시한다
