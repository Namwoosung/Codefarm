## Branch Naming Convention

본 프로젝트는 frontend와 backend를 하나의 레포지토리에서 관리한다.
따라서 feature 브랜치는 작업 범위(Frontend/Backend)와 도메인을 명확히 구분하여 네이밍한다.

### 1) 기본 규칙

* 브랜치명은 **소문자(kebab-case)** 를 사용한다.
* 슬래시(`/`)는 계층 구분에만 사용한다.
* 브랜치명은 “무엇을” 하는지 식별 가능해야 한다. (추상명 금지: `test`, `tmp`, `new` 등)

### 2) feature 브랜치 규칙 (모노레포 대응)

#### Frontend

```
feature/frontend/<task-name>
```

예시

* `feature/frontend/auth`
* `feature/frontend/dashboard`
* `feature/frontend/receipt`
* `feature/frontend/common`

#### Backend

```
feature/backend/<task-name>
```

예시

* `feature/backend/auth`
* `feature/backend/ledger`
* `feature/backend/receipt`
* `feature/backend/common`

> `<task-name>`: 작업 (예: dashboard, receipt)

### 3) infra / fix / hotfix 브랜치 규칙

#### infra

```
infra/<scope>/<task-name>
```

예시

* `infra/ci/branch-rules`
* `infra/deploy/dev-prod-scripts`
* `infra/nginx/reverse-proxy-conf`

#### fix (develop 기준 버그)

```
fix/<scope>/<issue-summary>
```

예시

* `fix/frontend/auth-login-validation`
* `fix/backend/ledger-null-pointer`
* `fix/common/env-parsing`

#### hotfix (main 기준 운영 긴급)

```
hotfix/<issue-summary>
```

예시

* `hotfix/payment-500-error`
* `hotfix/login-redirect-bug`

### 4) 병합 규칙(요약)

* `feature/*`, `infra/*`, `fix/*` → **develop** 로 Merge Request 병합
* `hotfix/*` → **main** 으로 병합(필요 시 develop에도 역병합)
* main 브랜치는 직접 push 금지(예외 규칙은 별도 정책 참조)

### 5) 권장 도메인 예시

* `auth` : 로그인/권한
* `receipt` : 영수증/업로드/OCR
* `ledger` : 장부/정산
* `dashboard` : 대시보드/지표
* `common` : 공통(UI 컴포넌트, 예외처리 등)
* `infra` : CI/CD, 서버, 배포, 설정

### 6) (선택) Issue 키 포함 규칙

이슈 트래킹(Jira 등)을 사용하는 경우 브랜치에 키를 포함할 수 있다.

Frontend 예시

* `feature/frontend/auth/login-ui-SSR-123`

Backend 예시

* `feature/backend/receipt/ocr-parser-SSR-208`


### Commit Message Convention

- 태그는 6개중 하나 사용(fix, feature, refactor, docs, chore, ci)
- 태그는 소문자
- 내용은 영어로 작성, 동사로 시작
- 예시
    - feat(backend): add controller advice
    - docs(infra): update commit message convention to README