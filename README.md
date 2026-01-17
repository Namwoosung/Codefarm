## Branch Strategy

본 프로젝트는 Gitflow 기반의 브랜치 전략을 사용한다.

- develop: 개발 및 통합 테스트용 브랜치
- main: 운영 배포 전용 브랜치
- feature/*: 기능 개발 브랜치 (develop으로 병합)
- infra/*: 인프라 설정 및 배포 관련 작업 브랜치 (develop으로 병합)
- fix/*: 개발 환경 내 버그 수정 브랜치 (develop으로 병합)
- hotfix/*: 운영 환경 긴급 수정 브랜치 (main 기준 생성)

main 브랜치는 Maintainer를 포함하여 직접 push를 원칙적으로 금지한다.
모든 변경은 Merge Request를 통해 이루어지며,
단 문서 수정 또는 긴급 장애 대응 시에는 예외를 둘 수 있다.