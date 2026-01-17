## Infrastructure Overview

이 문서는 본 프로젝트의 인프라 구성과 배포 · 운영과 관련된 설정을 설명한다.

애플리케이션 로직이 아닌, CI/CD, Docker, 서버 환경 설정을 이해하는 것을 목표로 한다.

## Directory Structure

```md
repo-root/
├── src/                    # 애플리케이션 코드
├── Dockerfile              # 컨테이너 정의 (루트)
├── docker-compose.yml      # 서비스 조합 (루트)
├── .gitlab-ci.yml          # CI/CD 파이프라인 (루트)
├── infra/                  # 인프라 보조 파일만
│   ├── nginx/              # Reverse Proxy 설정
│   │   └── nginx.conf
│   ├── scripts/            # 배포 및 운영 스크립트
│   │   ├── deploy.sh
│   │   ├── deploy-dev.sh
│   │   ├── deploy-prod.sh
│   │   ├── rollback.sh
│   │   └── healthcheck.sh
│   └── README.md
└── README.md
```

## CI/CD Pipeline Overview

본 프로젝트는 GitLab CI/CD를 사용하며,
브랜치 역할에 따라 파이프라인의 실행 범위를 분리한다.

- feature / infra / fix
  - build + fast test
  - 배포 단계 없음

- develop
  - build + full test
  - dev 서버 자동 배포

- main
  - build + full test
  - prod 서버 manual 배포

- hotfix/*
  - main과 동일한 테스트 정책 적용
  - prod 서버 manual 배포


## Deployment Strategy

### Dev Environment
- 대상 브랜치: develop
- 서버: dev EC2
- 배포 경로: /srv/app
- 배포 방식: SSH 접속 후 git pull
- 인증: Deploy Token 기반 비대화형 인증

### Prod Environment
- 대상 브랜치: main, hotfix/*
- 서버: prod EC2
- 배포 경로: /srv/app
- 배포 방식: manual trigger 후 SSH 배포
- 인증: Deploy Token 기반 비대화형 인증

## Docker

- Dockerfile은 repository root에 위치한다.
- develop 브랜치 기준 이미지는 develop-latest 태그를 사용한다.
- prod 배포 시에는 main-latest 또는 버전 태그를 사용한다.

## Environment Variables & Security

- 민감 정보(SSH Key, Token)는 GitLab CI/CD Variables로 관리한다.
- prod 관련 변수는 Protected 설정을 적용한다.
- 서버 접근은 SSH key 기반으로 제한한다.
- 배포용 토큰은 read-only 권한을 원칙으로 한다.

## Operational Notes

- 서버 초기 세팅 시 /srv/app 디렉토리를 사전에 생성한다.
- git pull 실패 시 ~/.netrc 설정을 우선 확인한다.
- 배포 실패 시 CI 로그 → 서버 로그 순으로 확인한다.
