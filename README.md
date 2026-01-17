## Branch Strategy

본 프로젝트는 Gitflow를 단순화한 브랜치 전략을 사용하며, CI/CD 및 배포 자동화에 적합하도록 일부 규칙을 조정하였다.

- develop: 개발 및 통합 테스트용 브랜치
- main: 운영 배포 전용 브랜치
- feature/*: 기능 개발 브랜치 (develop으로 병합)
- infra/*: 인프라 설정 및 배포 관련 작업 브랜치 (develop으로 병합)
- fix/*: 개발 환경 내 버그 수정 브랜치 (develop으로 병합)
- hotfix/*: 운영 환경 긴급 수정 브랜치 (main 기준 생성)

main 브랜치는 Maintainer를 포함하여 직접 push를 원칙적으로 금지한다.
모든 변경은 Merge Request를 통해 이루어지며,
단 문서 수정 또는 긴급 장애 대응 시에는 예외를 둘 수 있다.

## CI/CD Pipeline Policy

본 프로젝트는 GitLab CI/CD를 사용하여 브랜치 역할에 따라 파이프라인의 실행 범위와 배포 전략을 분리한다.

- develop / main / hotfix 브랜치
  - 신뢰성 최우선 브랜치
  - build → full test 파이프라인 수행
  - 배포 단계 포함

- feature/* / infra/* / fix/* 브랜치
  - 빠른 피드백 우선 브랜치
  - build → fast test 파이프라인 수행
  - 배포 단계 미포함

## Deployment Strategy

본 프로젝트는 개발 환경(dev)과 운영 환경(prod)을 분리하여 배포한다.

- develop 브랜치
  - dev 서버로 자동 배포
  - 통합 테스트 및 기능 검증 목적

- main 브랜치
  - prod 서버 배포 대상
  - 배포는 manual job으로 수행하여 운영 안정성을 확보

- hotfix/* 브랜치
  - 운영 환경 긴급 수정용
  - main 브랜치와 동일한 테스트 정책 적용
  - prod 배포는 manual로 수행

## Security & Access Policy

- main 브랜치와 배포 관련 CI 변수는 Protected 설정을 적용한다.
- 운영 배포(prod)는 반드시 Maintainer 권한에서만 수행한다.
- 서버 배포는 비대화형 인증 방식으로 자동화되어 있으며, 토큰 및 키 정보는 GitLab CI/CD Variables를 통해 관리한다.