## Branch Naming Convention

본 프로젝트는 **Frontend / Backend를 하나의 모노레포(Monorepo)** 로 관리한다.
따라서 브랜치 네이밍 단계에서 **작업 범위와 책임 영역을 명확히 식별**할 수 있도록 규칙을 정의한다.

### 1) 기본 규칙

* 브랜치명은 **소문자(kebab-case)** 를 기본으로 사용한다.
* 슬래시(`/`)는 **계층 구분 용도**로만 사용한다.
* **계층 깊이는 최대 3단계까지만 허용**한다.

  ```
  <type>/<scope>/<task>
  ```
* **3번째 계층(task)** 에서 단어 구분이 필요한 경우
  하이픈(`-`) 대신 **camelCase** 를 사용한다.
* 브랜치명은 반드시 **“무엇을 하는 작업인지” 식별 가능**해야 한다.

  * ❌ 금지 예시: `test`, `tmp`, `new`, `fix1`
  * ✅ 권장: `authLogin`, `receiptParser`, `ledgerSettlement`

### 2) feature 브랜치 규칙 (모노레포 대응)

#### Frontend

```
feature/frontend/<task-name>
```

예시

* `feature/frontend/auth`
* `feature/frontend/dashboard`
* `feature/frontend/receiptUpload`
* `feature/frontend/commonUI`

#### Backend

```
feature/backend/<task-name>
```

예시

* `feature/backend/auth`
* `feature/backend/ledgerSettlement`
* `feature/backend/receiptParser`
* `feature/backend/common`

> `<task-name>`
>
> * 기능 또는 도메인 단위 작업
> * 필요 시 camelCase 사용 허용

### 3) infra / fix / hotfix 브랜치 규칙

#### infra (인프라 및 운영 구성)

```
infra/<scope>/<task-name>
```

예시

* `infra/ci/branchRules`
* `infra/deploy/devProdScripts`
* `infra/nginx/reverseProxyConf`

> scope 예시: `ci`, `deploy`, `nginx`, `docker`, `monitoring`

#### fix (develop 기준 버그 수정)

```
fix/<scope>/<issue-summary>
```

예시

* `fix/frontend/authLoginValidation`
* `fix/backend/ledgerNullPointer`
* `fix/common/envParsing`

#### hotfix (main 기준 운영 긴급 수정)

```
hotfix/<issue-summary>
```

예시

* `hotfix/payment500Error`
* `hotfix/loginRedirectBug`

---

### 4) 병합 규칙 (요약)

* `feature/*`, `infra/*`, `fix/*`
  → **develop 브랜치로 Merge Request**
* `hotfix/*`
  → **main 브랜치로 Merge**
  → 필요 시 develop 브랜치에 **역병합**
* **main 브랜치 직접 push 금지**

  * (예외는 별도 운영 정책 문서 참조)

### 5) 권장 도메인(scope) 예시

* `auth` : 인증 / 권한
* `receipt` : 영수증 / 업로드 / OCR
* `ledger` : 장부 / 정산
* `dashboard` : 대시보드 / 지표
* `common` : 공통 로직 / UI / 예외 처리
* `infra` : CI/CD, 서버, 배포, 설정

### 6) (선택) Issue Key 포함 규칙

이슈 트래킹 도구(Jira 등)를 사용하는 경우
**브랜치명 마지막에 Issue Key를 추가**할 수 있다.

Frontend 예시

```
feature/frontend/authLogin-SSR-123
```

Backend 예시

```
feature/backend/receiptParser-SSR-208
```

## Commit Message Convention

* 태그는 아래 **6개 중 하나만 사용**

  ```
  feat | fix | refactor | docs | chore | ci
  ```
* 태그는 **소문자**
* 커밋 메시지는 **영어**, **동사로 시작**
* 포맷

  ```
  <type>(scope): <message>
  ```

예시

* `feat(backend): add controller advice`
* `docs(infra): update branch naming convention`
* `fix(frontend): resolve login validation issue`