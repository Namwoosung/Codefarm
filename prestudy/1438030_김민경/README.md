### PRELIMINARY STUDY 1438030

# DeepSeek 기반 코딩 코칭 LLM 설계 학습 정리

## 1. 학습 목적
**DeepSeek LLM을 활용하여 알고리즘 코드 교육을 위한 ‘코칭 에이전트’를 설계하기 위해 학습한 내용**

단순히 정답을 생성하는 챗봇이 아니라,  
> **학생이 작성 중인 코드 상태를 분석하고 문제 난이도와 학습 수준에 맞는 ‘힌트 형태의 피드백’을 제공하는 시스템**  

을 만드는 것이 목표이다.

- LLM이 언제, 무엇을, 어느 수준으로 말해야 하는가?
- 정답을 주지 않으면서도 학습을 도울 수 있는 피드백은 무엇인가?
- DeepSeek 같은 추론형 LLM을 교육적으로 안전하게 사용하는 방법은 무엇인가?

---

## 2. 코딩 코칭 LLM의 본질적 문제 정의

### 2.1 정답 생성 vs 코칭 피드백

일반적인 LLM 사용:
- 질문 → 정답 생성

코딩 코칭 LLM:
- 문제 + 현재 코드 → **사고 방향을 교정하는 피드백 제공**

즉, 목표는 정답이 아니라:
- 문제를 어떻게 구조화해야 하는지
- 현재 접근이 맞는지/틀린지
- 다음에 무엇을 점검해야 하는지

👉 **코칭 LLM은 생성 문제가 아니라 ‘판단 + 통제’ 문제**

---

## 3. DeepSeek 모델 이해와 활용 방향

### 3.1 DeepSeek의 특징
- 강력한 추론(reasoning) 성향
- 코드 이해 및 오류 추론 능력 우수
- 단점: 통제하지 않으면 과도한 설명, 정답 유출 위험

### 3.2 교육적 활용의 핵심 전략
- **생각은 깊게, 출력은 제한적으로**
- 내부 추론은 허용하되, 사용자 출력은 힌트 규격으로 제한

이를 위해 다음을 학습함:
- Instruction hierarchy (System > Developer > User)
- Structured Output (JSON schema 강제)
- Reasoning 결과를 직접 노출하지 않는 Distillation 전략

---

## 4. LLM 출력 통제와 힌트 레벨 설계

### 4.1 힌트 레벨의 필요성

학생 수준과 문제 난이도가 다름에도 동일한 피드백을 주면:
- 초보자 → 좌절
- 중·고급자 → 성장 정체

따라서 힌트 강도를 명시적으로 설계함.

### 4.2 힌트 레벨 정의 (L1~L4)

- **L1: 방향 제시**
  - 문제를 어떤 관점으로 봐야 하는지
  - 어떤 값/구조가 핵심인지

- **L2: 다음 행동 힌트**
  - 지금 코드에서 무엇을 먼저 점검할지
  - 체크리스트 형태

- **L3: 국소적 오류 지적**
  - 특정 조건/루프/상태에서 문제가 있을 가능성 제시
  - 정답 코드 제공은 금지

- **L4: 잘못된 접근 경고**
  - 접근 자체가 성립하지 않는 이유 설명
  - 방향 전환 유도

👉 힌트 레벨은 모델이 “생성”하는 것이 아니라  
**정책에 의해 “선택”되도록 설계**

---

## 5. 알고리즘 코칭에서 가장 중요한 개념: 오류 유형(Taxonomy)

### 5.1 왜 오류 유형이 중요한가

“틀렸습니다”는 피드백이 아니다.  
좋은 코칭은 항상 **왜 틀렸는지의 유형을 전제**한다.

### 5.2 주요 오류 유형 정리

- 구현 오류
  - off-by-one
  - 초기화 누락
  - visited 처리 위치 오류

- 구조적 오류
  - DP 상태 정의 실패
  - BFS/DFS 선택 오류

- 전략 오류
  - 그리디 오판
  - 시뮬레이션 남용

- 성능 오류
  - 시간복잡도 오판
  - 불필요한 중첩 루프

### 5.3 설계에의 적용
- `issue_type` 라벨
- `wrong_direction` 판단
- 힌트 레벨 결정의 핵심 근거

---

## 6. 단계별 피드백 이론 (교육학 관점)

### 6.1 즉각적 피드백 vs 지연 피드백

- **개념 문제 / 초보자**
  - 즉각적 + 명시적 피드백 필요
  - 사고 틀(template)을 제공해야 함

- **중급 이상**
  - 질문형, 지연 피드백이 효과적
  - 스스로 사고하게 만드는 것이 목적

### 6.2 메타인지 유도
- “왜 이 접근이 실패하는지 설명할 수 있는가?”
- “이 문제와 비슷한 문제를 본 적이 있는가?”

👉 문제 난이도 × 코드 진행도 × 힌트 레벨을 함께 고려해야 함

---

## 7. 단일 LLM + 경량 분류기 구조를 선택한 이유

### 7.1 왜 모든 판단을 LLM에 맡기지 않는가
- 비용 증가
- 출력 일관성 붕괴
- 스포일러 위험 증가

### 7.2 경량 분류기의 역할
- 코드 정적 분석(AST)
  - 루프 깊이
  - 재귀 여부
  - 자료구조 사용 여부
- 실행 결과 기반 분기
  - CE / RE / TLE / WA

### 7.3 역할 분리 구조

```text
입력(문제 + 코드)
 → 정적 분석
 → 경량 분류(진행도/방향)
 → DeepSeek 진단
 → 힌트 생성
 → 정책 검증


### 8. 데이터 스키마
```
{
  "id": "hintreq_20260116_000123",
  "problem": {
    "problem_id": "p_001",
    "source": "internal",
    "title": "Two Sum Variant",
    "statement": "...",
    "io": {
      "input": "...",
      "output": "..."
    },
    "constraints": {
      "n_max": 200000,
      "value_range": [-1000000000, 1000000000]
    },
    "examples": [
      { "input": "5\n1 2 3 4 5\n", "output": "..." }
    ],
    "tags": ["array", "two_pointers"],
    "difficulty": "intermediate"
  },

  "student": {
    "student_id_hash": "sha256:....",
    "level": "beginner",
    "language": "python",
    "session_id": "sess_abc",
    "attempt_index": 3,
    "time_from_start_sec": 840
  },

  "submission": {
    "code_snapshot": "def solve():\n  ...",
    "run_result": {
      "verdict": "WA",
      "compiler_error": null,
      "runtime_error": null,
      "time_ms": 120,
      "memory_kb": 20480,
      "failed_case": {
        "input": "....",
        "expected": "....",
        "actual": "...."
      }
    }
  },

  "labels": {
    "progress_stage": "partial_correct",
    "issue_type": ["edge_case", "off_by_one"],
    "wrong_direction": false,
    "spoiler_risk": "mid"
  },

  "hint_policy": {
    "requested_hint_level": "L2",
    "max_hint_level_allowed": "L2"
  },

  "gold": {
    "diagnosis_json": {
      "main_issue": "off_by_one",
      "where_to_check": ["loop boundary", "index update"],
      "confidence": 0.72
    },
    "hint_text": {
      "one_line_diagnosis": "접근은 맞지만 포인터/인덱스 갱신 경계에서 한 칸씩 밀릴 가능성이 큽니다.",
      "next_actions": [
        "루프 종료 조건이 n-1 / n 중 무엇을 의미하는지 예시 입력으로 추적해 보세요.",
        "포인터를 이동시키는 조건이 '==' 포함 여부에 따라 어떤 케이스가 누락되는지 확인하세요."
      ],
      "question": "지금 코드에서 포인터가 이동하는 순간, 불변식(invariant)이 유지된다고 말할 수 있나요?",
      "warning_or_counterexample": "값이 중복되는 입력에서 한 번만 매칭해야 하는 조건이 있다면 경계가 깨집니다."
    }
  },

  "preference": {
    "candidates": [
      { "id": "A", "hint": "...", "violations": [] },
      { "id": "B", "hint": "...", "violations": ["too_specific"] }
    ],
    "chosen": "A",
    "rationale_tags": ["actionable", "level_match"]
  }
}
```

#### 이 스키마의 장점:
- SFT(정답 라벨)도 되고
- Preference(선호 비교)도 되고
- 운영 로그(개선 여부)로 평가까지 연결됩니다.

#### 라벨(정답) 설계: “무엇을 사람이 붙이고, 무엇을 자동화할지”
- 사람이 붙이면 좋은 라벨(가치 높음)
- progress_stage (진행도)
- wrong_direction (완전 잘못된 접근 여부)
- hint_level (L1~L4)
- 스포일러 여부/정책 위반 태그

#### 자동화가 가능한 라벨(비용 절감)
- verdict(CE/RE/TLE/WA): 채점기로 자동 수집
- 시간/메모리, 컴파일 메시지
- 정적 분석(파이썬 AST/자바 파서)로 “루프 중첩 깊이, 재귀 사용 여부” 등 특징 추출
- 권장 전략은 사람 라벨 최소화 + 자동 특징 최대화입니다.
