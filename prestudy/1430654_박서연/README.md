### PRELIMINARY STUDY 1430654
# Frontend UI & Tech Research

## 1. UI / UX 디자인 리서치 (Neumorphism 중심)

### 🎨 Design Keyword

* **Neumorphism (뉴모피즘)**

  * Soft UI, 낮은 대비
  * 그림자 기반 입체감 (inner / outer shadow)
  * 카드, 버튼, 입력창 중심의 미니멀 UI

---

### 1.1. Web Design Reference

* [https://themovingposter.com/](https://themovingposter.com/)
* [https://www.awwwards.com/websites/webflow/](https://www.awwwards.com/websites/webflow/)
* [https://www.behance.net/](https://www.behance.net/)
* [https://kr.pinterest.com/](https://kr.pinterest.com/)

---

### 1.2. Color & Accessibility

* 컬러 팔레트 참고: [https://colorhunt.co/](https://colorhunt.co/)
* 명도 대비 체크: [https://colourcontrast.cc/](https://colourcontrast.cc/)

> 뉴모피즘 특성상 대비가 약해질 수 있으므로, 접근성(가독성) 검증 필수

---

### 1.3. Calendar UI Reference

* [https://www.behance.net/gallery/183223195/Calendar-UI](https://www.behance.net/gallery/183223195/Calendar-UI)

#### Calendar Screen Type

```text
MonthView / WeekView / DayView
```

---

### 🎞 Frontend Animation Reference

#### Motion One

* GSAP 대비 가벼운 애니메이션 라이브러리
* UI 인터랙션, 토글, 미세한 모션에 적합
* [https://motion.oku-ui.com/](https://motion.oku-ui.com/)

#### GSAP

* 복잡한 타임라인, 스크롤 인터랙션에 강점
* [https://gsap.com/showcase/](https://gsap.com/showcase/)

---

### Vue 애니메이션 선택 가이드

| 프로젝트 성격             | 추천 라이브러리           |
| ------------------- | ------------------ |
| 단일 페이지 랜딩 / 브랜딩     | GSAP               |
| 간단한 UI 반응, 버튼, 토글   | Motion One         |
| 스크롤 기반 인터랙션         | GSAP ScrollTrigger |
| SPA 라우팅 전환          | GSAP Timeline      |
| 모바일 웹 / 성능 민감       | Motion One         |
| 3D / Canvas / WebGL | GSAP               |

출처: [https://twentytwentyone.tistory.com/1764](https://twentytwentyone.tistory.com/1764)

---

## 2. FE 기술 사항 정리

### 2.1. 공통 기술 스택

* **Framework**: Vue.js (Composition API)
* **Build Tool**: Vite
* **State Management**: Pinia
* **HTTP Communication**: Axios

---

### 2.2. UI / Interaction

* **Styling**: Tailwind CSS + Headless UI
* **Icon**: Lucide Icons

  * [https://lucide.dev/icons/](https://lucide.dev/icons/)
* **에이전트 / 오케스트레이션 시각화**: Vue Flow

  * 노드 기반 흐름, 상태 시각화에 활용

---

### 2.3. Chat / Agent UI

* **vue-virtual-scroller**

  * 대량 메시지 렌더링 최적화
  * 화면에 노출되는 영역 기준으로 DOM 교체
* **오케스트레이션 UI**

  * Agent 상태, 메시지 흐름 시각화 목적

---

### 2.4. Calendar

* Month / Week / Day View 지원 구조
* 일정 단위 컴포넌트화
* 추후 드래그, 애니메이션 확장 고려

---

