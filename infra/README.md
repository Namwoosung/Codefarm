# Infrastructure Overview

이 문서는 본 프로젝트의 인프라 구성과  
CI/CD, 배포 및 운영 방식에 대한 **최종 기준 문서**이다.

본 문서는 애플리케이션 비즈니스 로직이 아닌,

- GitLab CI/CD 파이프라인
- Docker 이미지 빌드 및 배포 전략
- EC2 서버 디렉토리 구조(`/srv/app`)
- Docker Compose 역할 분리 (foundation / application / inference)
- 배포·헬스체크·롤백 스크립트 기준
- Nginx 기반 SSE(Server-Sent Events) 운영 정책
- GPU 추론 서버(Inference) 운영 및 모델 배포 전략

을 이해하는 것을 목표로 한다.

## 1. Current Server Directory Structure

본 프로젝트는 **단일 EC2 인스턴스 + GPU 서버** 구조로 운영되며,  
기본 애플리케이션 서버 기준 디렉토리는 `/srv/app` 이다.

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

배포 구조는 **Foundation / Application / Inference**의 3개 레이어로 구성된다.

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
* Application / Inference 배포와 독립
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

* CI/CD를 통한 자동 배포
* develop → 자동
* main/hotfix → manual
* Foundation과 동일한 외부 네트워크(`appnet`) 사용

### 2.3 Inference Layer (GPU 추론 서버)

Inference 레이어는 **GPU 서버에서 별도로 운영되는 추론 전용 서비스**이다.

* FastAPI 기반 추론 API
* GPU 자원(MIG 포함)을 사용
* Docker Compose를 사용하지 않고 **서버 디렉토리 기반 배포** 방식 채택

## 3. GPU Inference Server Structure

GPU 서버 내 추론 서비스 기준 경로는 다음과 같다.

```text
/srv/app/app/inference
├── app.py                  # FastAPI 엔트리포인트
├── requirements.txt
├── READMD.md               # inference 전용 문서
├── models/
│   ├── label_model/        # label 모델 (unzipped)
│   ├── text_model/         # text 모델 (fold별 adapter)
│   ├── model1.py
│   ├── model2.py
│   └── __pycache__/
├── utils/
│   ├── auth.py
│   ├── constant.py
│   ├── json_utils.py
│   ├── labels.py
│   ├── prompt_builder.py
│   └── prompt.py
└── __pycache__/
```

## 4. Inference Model Management Policy

### 4.1 모델 저장 위치

대용량 모델 파일은 Git 저장소에 포함하지 않는다.

* GPU 서버 홈 디렉토리 기준:

  * `~/models/label_model.zip`
  * `~/models/text_model.zip`

### 4.2 모델 배포 방식

Inference 배포 시 CI 파이프라인에서 다음 순서로 처리한다.

1. Git 저장소에서 **inference 디렉토리만 sparse checkout**
2. 서버의 `/srv/app/app/inference`로 코드 동기화
3. `~/models/*.zip` 파일을 inference 디렉토리 하위로 unzip

즉,

* **코드** → Git 기반 배포
* **모델** → 서버 로컬 자산으로 관리

이 방식을 통해:

* 대용량 모델로 인한 Git 저장소 비대화 방지
* 코드/모델 배포 책임 분리
* 추론 코드만 빠르게 교체 가능

## 5. CI/CD Pipeline – Inference Stage

`.gitlab-ci.yml`에는 `inference` 스테이지가 별도로 정의되어 있다.

Inference 배포 특징:

* `GIT_STRATEGY: none`
* `git sparse-checkout` 사용
* inference 디렉토리만 fetch
* GPU 서버에 rsync 방식으로 반영
* Pyenv 기반 가상환경(`venv`) 활성화 후 의존성 설치
* 모델 zip 파일 unzip 후 즉시 사용 가능 상태로 전환

Inference 레이어는 **Application 배포와 완전히 독립적**이다.

## 6. Nginx & SSE(Server-Sent Events) 운영 정책

### 6.1 문제 배경

배포 환경에서 **SSE 기반 스트리밍 응답이 전달되지 않는 문제**가 발생했다.

* 로컬 환경: 정상
* 배포 환경(Nginx 경유): 첫 이벤트(CONNECTED) 미수신 또는 지연

원인:

* Nginx 기본 프록시 동작

  * 응답 버퍼링
  * 캐시
  * Connection 헤더 처리
    가 SSE 특성과 맞지 않음

### 6.2 해결 전략

* SSE 엔드포인트를 **전용 location으로 분리**
* SSE 특성에 맞게 프록시 동작을 명시적으로 제어

적용 정책:

* `proxy_buffering off`
* `proxy_cache off`
* `proxy_request_buffering off`
* `Connection: keep-alive` 명시
* `Upgrade` 헤더 제거 (SSE는 WebSocket 아님)
* `X-Accel-Buffering: no` 헤더 추가

결과:

* 첫 이벤트 즉시 전달
* 장시간 연결 안정화
* 일반 REST API와 설정 충돌 제거

## 7. Minimal Rules (Team Agreement)

* 서버 운영 기준 경로는 `/srv/app`
* app 배포

  * develop: 자동
  * main/hotfix: 수동
* foundation은 필요 시에만 수동 배포
* inference는 별도 GPU 서버에서 독립 운영
* `.env`는 서버에만 존재
* 민감 정보는 GitLab Variables로 관리
* 컨테이너 런타임 환경변수는 반드시 명시적으로 주입
* **SSE 엔드포인트는 반드시 전용 Nginx 설정을 사용**
* **대용량 모델은 Git에 포함하지 않는다**