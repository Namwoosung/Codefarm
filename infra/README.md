# Infrastructure Overview

이 문서는 본 프로젝트의 인프라 구성과  
CI/CD, 배포 및 운영과 관련된 설정을 설명한다.

애플리케이션 비즈니스 로직이 아닌,  
GitLab CI/CD, 서버 환경, 배포 흐름을 이해하는 것을 목표로 한다.

## Directory Structure

```bash
repo-root/
├── src/                    # 애플리케이션 코드
├── Dockerfile              
├── docker-compose.yml      
├── .gitlab-ci.yml          # CI/CD 파이프라인 (루트)
├── infra/                  # 인프라 및 운영 관련 파일
│   ├── nginx/              # Reverse Proxy 설정
│   │   └── nginx.conf
│   ├── scripts/            # 배포 및 운영 스크립트
│   │   ├── deploy.sh
│   │   ├── deploy-dev.sh
│   │   ├── deploy-prod.sh
│   │   ├── rollback.sh
│   │   └── healthcheck.sh
│   └── README.md           # 인프라 문서 (본 문서)
└── README.md               # 프로젝트 전반 문서
```

## Branch Strategy (Infra Perspective)

본 프로젝트는 Gitflow를 단순화한 브랜치 전략을 사용하며,  
CI/CD 및 배포 자동화에 적합하도록 규칙을 조정하였다.

### Branch Roles

- **feature/***  
  기능 개발 브랜치 → develop 병합

- **infra/***  
  CI/CD, 배포, 서버 환경, 설정 변경 → develop 병합

- **fix/***  
  개발 환경 버그 수정 → develop 병합

- **develop**  
  통합 및 검증 브랜치 (dev 환경 자동 배포)

- **hotfix/***  
  운영 환경 긴급 수정 브랜치 (main 기준 생성)

- **main**  
  운영(Production) 배포 전용 브랜치

### Main Branch Protection

- main 브랜치는 Maintainer를 포함하여 **직접 push를 금지**한다.
- 모든 변경 사항은 **Merge Request(MR)** 를 통해 반영한다.
- 문서 수정 또는 긴급 장애 대응의 경우 예외를 둘 수 있다.

## CI/CD Pipeline Overview

본 프로젝트는 GitLab CI/CD를 사용하며,  
브랜치 역할에 따라 파이프라인의 실행 범위와 강도를 분리한다.

- **feature / infra / fix**
  - build + fast test
  - 배포 단계 없음

- **develop**
  - build + full test
  - dev 서버 자동 배포

- **main**
  - build + full test
  - prod 서버 manual 배포

- **hotfix/***
  - main과 동일한 테스트 정책
  - prod 서버 manual 배포

## Deployment Strategy

### Dev Environment

- 대상 브랜치: develop
- 서버: dev EC2
- 배포 경로: `/srv/app`
- 배포 방식:
  - GitLab CI → SSH 접속
  - 서버 내 배포 스크립트 실행
- 인증 방식:
  - Deploy Token 기반 비대화형 인증

### Prod Environment

- 대상 브랜치: main, hotfix/*
- 서버: prod EC2
- 배포 경로: `/srv/app`
- 배포 방식:
  - GitLab CI manual trigger
  - SSH 접속 후 배포 스크립트 실행
- 인증 방식:
  - Deploy Token 기반 비대화형 인증

## Deployment Scripts

배포 및 운영 로직은 `infra/scripts` 디렉토리의 스크립트로 분리한다.

- **deploy.sh**  
  dev / prod 공통 배포 로직

- **deploy-dev.sh**  
  dev 환경 배포 전용 스크립트

- **deploy-prod.sh**  
  prod 환경 배포 전용 스크립트

- **healthcheck.sh**  
  배포 후 기본 상태 점검

- **rollback.sh**  
  배포 실패 또는 장애 시 롤백용 스크립트

CI/CD 파이프라인에서는  
직접 배포 로직을 작성하지 않고,  
서버에 존재하는 스크립트를 호출하는 방식을 사용한다.

## Environment Variables & Security

- 민감 정보(SSH Key, Deploy Token)는  
  GitLab CI/CD Variables로 관리한다.
- prod 관련 변수는 **Protected** 설정을 적용한다.
- 서버 접근은 SSH key 기반으로 제한한다.
- 배포용 토큰은 **read-only 권한**을 원칙으로 한다.
- main 브랜치는 직접 push를 금지한다.

## Operational Notes

- 서버 초기 세팅 시 `/srv/app` 디렉토리를 사전에 생성한다.
- 배포 스크립트 실행 권한은 서버별로 최초 1회 설정한다.

```bash
chmod +x /src/app/infra/scripts/*.sh
````

* git pull 실패 시 `~/.netrc` 설정을 우선 확인한다.
* 배포 실패 시 다음 순서로 문제를 추적한다.

  1. GitLab CI 로그 확인
  2. 서버 로그 확인