### PRELIMINARY STUDY 1438030

# Deepseek을 이용한 코드 피드백 모델 만들기

### 







### 데이터 스키마
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
