<div align="center">
  <img src="./assets/logo.png" alt="logo" />
  <h3>내 곁에 따듯한 코딩 선생님, 코드팜</h3>
  <h4>학생들을 위한 실시간 <b>AI 문제 풀이 코칭 서비스</b>입니다.</h4>
</div>

<br/>

- **개발 기간** : 2026.01.19 ~ 2026.02.06 **(3주)**
- **플랫폼** : Web
- **개발 인원** : 6명
- **기관** : 삼성 청년 SW · AI 아카데미 14기

<br/>

<div align="center">
  <img src="./assets/homepage.png" alt="homepage" />
</div>

---

## 🔎 목차

- [🙌 팀원 구성](#-팀원-구성)
- [🪄 기술 스택](#-기술-스택)
- [🛠️ 아키텍처](#-아키텍처)
- [📲 기능 구성](#-기능-구성)
- [📂 디렉터리 구조](#-디렉터리-구조)
- [📦 프로젝트 산출물](#-프로젝트-산출물)

---

## 🙌 팀원 구성

<table align="center">
  <tr>
    <td align="center">
      <img src="./assets/park_seoyeon.jpg" width="240" height="280" alt="park_seoyeon" />
      <br/>
      <b>박서연</b>
      <ul>
        <li>프론트엔드 전반(Vue.js, Vite, Pinia) 구현</li>
        <li>서비스 비주얼 및 인터페이스 디자인</li>
      </ul>
    </td>
    <td align="center">
      <img src="./assets/choi_yeonjae.jpg" width="240" height="280" alt="choi_yeonjae" />
      <br/>
      <b>최연제</b>
      <ul>
        <li>프론트엔드 전반(Vue.js, Vite, Pinia) 구현</li>
        <li>IDE, 로드맵, 카드, 마이페이지, 힌트/피드백 UI 구현</li>
      </ul>
    </td>
    <td align="center">
      <img src="./assets/kim_minkyung.jpg" width="240" height="280" alt="kim_minkyung" />
      <br/>
      <b>김민경</b>
      <ul>
        <li>AI Inference 서버(FastAPI, PyTorch) 구현</li>
        <li>코드 피드백 서버(Feedback API) 및 힌트 생성 기능 구현</li>
      </ul>
    </td>
  </tr>

  <tr>
    <td align="center">
      <img src="./assets/nam_woosung.jpg" width="240" height="280" alt="nam_woosung" />
      <br/>
      <b>남우성</b>
      <ul>
        <li>백엔드(Spring Boot) Session, Hint, User, Card, Curriculum 구현</li>
        <li>Execution/Feedback 서버 연동 및 API 설계</li>
      </ul>
    </td>
    <td align="center">
      <img src="./assets/kim_hyeongtaek.jpg" width="240" height="280" alt="kim_hyeongtaek" />
      <br/>
      <b>김형택</b>
      <ul>
        <li>DevOps 인프라(GitLab CI/CD, Docker, Nginx) 전담 구축</li>
        <li>프로젝트 총괄 및 배포 워크플로우 관리</li>
      </ul>
    </td>
    <td align="center">
      <img src="./assets/jeong_mungi.jpg" width="240" height="280" alt="jeong_mungi" />
      <br/>
      <b>정문기</b>
      <ul>
        <li>데이터 파트 담당 및 AI 영역 협업</li>
        <li>AI Inference 서버 및 모델 로딩 최적화 구현</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🪄 기술 스택

<div align="center">

### 🫡 Frontend

<img src="https://img.shields.io/badge/html5-badge?style=for-the-badge&logo=html5&logoColor=white&color=%23E34F26"/>
<img src="https://img.shields.io/badge/css-badge?style=for-the-badge&logo=css&logoColor=white&color=%23663399"/>
<img src="https://img.shields.io/badge/javascript-badge?style=for-the-badge&logo=javascript&logoColor=white&color=%23F7DF1E"/>
<img src="https://img.shields.io/badge/vuedotjs-badge?style=for-the-badge&logo=vuedotjs&logoColor=white&color=%234FC08D"/>
<img src="https://img.shields.io/badge/pinia-badge?style=for-the-badge&logo=pinia&logoColor=white&color=%23FFD859"/>
<img src="https://img.shields.io/badge/vite-badge?style=for-the-badge&logo=vite&logoColor=white&color=%239135FF"/>
<img src="https://img.shields.io/badge/cursor-badge?style=for-the-badge&logo=cursor&logoColor=white&color=%23000000"/>

<table>
  <tr>
    <th>Category</th>
    <th>Specification</th>
  </tr>
  <tr>
    <td><b>Framework</b></td>
    <td>Vue 3.5.26</td>
  </tr>
  <tr>
    <td><b>Build Tool</b></td>
    <td>Vite 7.3.0</td>
  </tr>
  <tr>
    <td><b>State Management</b></td>
    <td>Pinia 3.0.4</td>
  </tr>
  <tr>
    <td><b>Router</b></td>
    <td>Vue Router 4.6.4</td>
  </tr>
  <tr>
    <td><b>CSS</b></td>
    <td>Tailwind CSS 4.1.18, DaisyUI 5.5.14, SASS</td>
  </tr>
  <tr>
    <td><b>Code Editor</b></td>
    <td>Monaco Editor 0.55.1</td>
  </tr>
    <td><b>Node.js</b></td>
    <td>^20.19.0 || >=22.12.0</td>
  </tr>
  <tr>
    <td><b>HTTP Client</b></td>
    <td>Axios 1.13.3</td>
  </tr>
  <tr>
    <td><b>Markdown / Sanitize</b></td>
    <td>marked 17.0.1, DOMPurify 3.2.7 (힌트·피드백 렌더링)</td>
  </tr>
  <tr>
    <td><b>Terminal (실행 결과)</b></td>
    <td>@xterm/xterm 6.0.0</td>
  </tr>
  <tr>
    <td><b>SSE</b></td>
    <td>eventsource-parser 3.0.6 (힌트 스트리밍)</td>
  </tr>
  <tr>
    <td><b>Lint / Format</b></td>
    <td>ESLint 9.39.2, Prettier 3.8.1</td>
  </tr>
  <tr>
    <td><b>Animation / Effect</b></td>
    <td>Vue Transition, Custom @keyframes, page-flip 2.0.7, canvas-confetti 1.9.4</td>
  </tr>
</table>

### 🤓 Backend

<img src="https://img.shields.io/badge/intellijidea-badge?style=for-the-badge&logo=intellijidea&logoColor=white&color=%23000000"/>
<img src="https://img.shields.io/badge/springboot-badge?style=for-the-badge&logo=springboot&logoColor=white"/>
<img src="https://img.shields.io/badge/gradle-badge?style=for-the-badge&logo=gradle&logoColor=white&color=%2302303A"/>
<img src="https://img.shields.io/badge/postgresql-badge?style=for-the-badge&logo=postgresql&logoColor=white&color=%234169E1"/>
<img src="https://img.shields.io/badge/redis-badge?style=for-the-badge&logo=redis&logoColor=white&color=%23FF4438"/>

<table>
  <tr>
    <th>Category</th>
    <th>Specification</th>
  </tr>
  <tr>
    <td><b>Framework</b></td>
    <td>Spring Boot 3.5.9</td>
  </tr>
  <tr>
    <td><b>Java</b></td>
    <td>Java 17</td>
  </tr>
  <tr>
    <td><b>Build Tool</b></td>
    <td>Gradle 8.x</td>
  </tr>
  <tr>
    <td><b>Database</b></td>
    <td>PostgreSQL</td>
  </tr>
  <tr>
    <td><b>Cache</b></td>
    <td>Redis (Spring Data Redis)</td>
  </tr>
  <tr>
    <td><b>ORM</b></td>
    <td>Spring Data JPA, QueryDSL 5.0.0</td>
  </tr>
  <tr>
    <td><b>Auth</b></td>
    <td>Spring Security, JJWT 0.11.5</td>
  </tr>
  <tr>
    <td><b>HTTP Client</b></td>
    <td>Spring WebFlux (WebClient)</td>
  </tr>
</table>

### 🧐 AI / Data

<img src="https://img.shields.io/badge/fastapi-badge?style=for-the-badge&logo=fastapi&logoColor=white&color=%23009688"/>
<img src="https://img.shields.io/badge/python-badge?style=for-the-badge&logo=python&logoColor=white&color=%233776AB"/>
<img src="https://img.shields.io/badge/pytorch-badge?style=for-the-badge&logo=pytorch&logoColor=white&color=%23EE4C2C"/>
<img src="https://img.shields.io/badge/codellama-%23000000.svg?style=for-the-badge&logo=ollama&logoColor=white"/>


<table>
  <tr>
    <th>Category</th>
    <th>Specification</th>
  </tr>
  <tr>
    <td><b>Framework</b></td>
    <td>FastAPI 0.128.0</td>
  </tr>
  <tr>
    <td><b>Runtime</b></td>
    <td>Uvicorn 0.40.0</td>
  </tr>
  <tr>
    <td><b>Deep Learning Env</b></td>
    <td>Python 3.11.9, PyTorch 2.7.0 (CUDA 12.8), Transformers 4.56.2</td>
  </tr>
  <tr>
    <td><b>Fine-tuning</b></td>
    <td>PEFT 0.18.1, BitsAndBytes 0.49.1, QLoRA</td>
  </tr>
  <tr>
    <td><b>Inference (힌트)</b></td>
    <td>Label Classifier(CodeLlama 7B), Text Generation(CodeLlama 3B)</td>
  </tr>
  <tr>
    <td><b>Feedback Server</b></td>
    <td>httpx, OpenAI API KEY(gpt-4o-mini)</td>
  </tr>
</table>

### 🥱 DevOps

<img src="https://img.shields.io/badge/docker-badge?style=for-the-badge&logo=docker&logoColor=white&color=%232496ED"/>
<img src="https://img.shields.io/badge/nginx-badge?style=for-the-badge&logo=nginx&logoColor=white&color=%23009639"/>
<img src="https://img.shields.io/badge/k6-badge?style=for-the-badge&logo=k6&logoColor=white&color=%237D64FF"/>
<img src="https://img.shields.io/badge/prometheus-badge?style=for-the-badge&logo=prometheus&logoColor=white&color=%23E6522C"/>
<img src="https://img.shields.io/badge/grafana-badge?style=for-the-badge&logo=grafana&logoColor=white&color=%23F46800"/>

<table>
  <tr>
    <th>Category</th>
    <th>Specification</th>
  </tr>
  <tr>
    <td><b>Instance Type</b></td>
    <td>AWS EC2 t2.xlarge</td>
  </tr>
  <tr>
    <td><b>CPU</b></td>
    <td>4 vCPUs</td>
  </tr>
  <tr>
    <td><b>RAM</b></td>
    <td>16 GB</td>
  </tr>
  <tr>
    <td><b>Storage</b></td>
    <td>SSD 320 GB</td>
  </tr>
  <tr>
    <td><b>Docker</b></td>
    <td>29.1.5</td>
  </tr>
  <tr>
    <td><b>Docker Compose</b></td>
    <td>v2.25.0</td>
  </tr>
  <tr>
    <td><b>CI/CD</b></td>
    <td>GitLab CI/CD</td>
  </tr>
  <tr>
    <td><b>CI Runner</b></td>
    <td>Self-hosted GitLab Runner (Docker executor)</td>
  </tr>
  <tr>
    <td><b>Nginx</b></td>
    <td>nginx/1.29.5</td>
  </tr>
  <tr>
    <td><b>K6</b></td>
    <td>v1.5.0</td>
  </tr>
  <tr>
    <td><b>Prometheus</b></td>
    <td>3.9.1</td>
  </tr>
  <tr>
    <td><b>Grafana</b></td>
    <td>12.3.2</td>
  </tr>
  <tr>
    <td><b>Webhook Handler</b></td>
    <td>Python 3.11-slim, FastAPI 0.128.0, Uvicorn[standard] 0.40.0</td>
  </tr>
</table>

### 😀 Collaboration

<img src="https://img.shields.io/badge/git-badge?style=for-the-badge&logo=git&logoColor=white&color=%23F05032"/>
<img src="https://img.shields.io/badge/gitlab-badge?style=for-the-badge&logo=gitlab&logoColor=white&color=%23FC6D26"/>
<img src="https://img.shields.io/badge/figma-badge?style=for-the-badge&logo=figma&logoColor=white&color=%23F24E1E"/>
<img src="https://img.shields.io/badge/notion-badge?style=for-the-badge&logo=notion&logoColor=white&color=%23000000"/>
<img src="https://img.shields.io/badge/jira-badge?style=for-the-badge&logo=jira&logoColor=white&color=%230052CC"/>

</div>

## 🛠️ 아키텍처

<img src="./assets/architecture.png"/>

## 📲 기능 구성

<div align="center">

|             모든 문제              |                 커리큘럼                 |
| :--------------------------------: | :--------------------------------------: |
| ![problems](./assets/problems.png) | ![curriculums](./assets/curriculums.png) |

|              로드맵              |             카드             |
| :------------------------------: | :--------------------------: |
| ![roadmap](./assets/roadmap.png) | ![cards](./assets/cards.png) |

|           마이페이지(내정보)            |            마이페이지(학습기록)             |
| :-------------------------------------: | :-----------------------------------------: |
| ![mypageInfo](./assets/mypage_info.png) | ![mypageRecord](./assets/mypage_record.png) |

|           IDE            |               실행하기               |
| :----------------------: | :----------------------------------: |
| ![ide](./assets/ide.png) | ![execution](./assets/execution.png) |

|             힌트             |               피드백               |
| :--------------------------: | :--------------------------------: |
| ![hints](./assets/hints.png) | ![feedback](./assets/feedback.png) |

</div>

## 📂 디렉터리 구조

### GitLab Repository

<details>
  <summary>
    assets
  </summary>
  
  ```
  ./assets
  |-- architecture.png
  |-- cards.png
  |-- choi_yeonjae.jpg
  |-- curriculums.png
  |-- execution.png
  |-- feedback.png
  |-- hints.png
  |-- homepage.png
  |-- ide.png
  |-- jeong_mungi.jpg
  |-- kim_hyeongtaek.jpg
  |-- kim_minkyung.jpg
  |-- logo.png
  |-- mypage_info.png
  |-- mypage_record.png
  |-- nam_woosung.jpg
  |-- park_seoyeon.jpg
  |-- problems.png
  `-- roadmap.png
  ```

</details>
<details>
  <summary>
    backend
  </summary>

```
./backend
|-- .dockerignore
|-- .gitattributes
|-- .gitignore
|-- .gradle
|   |-- 8.14.3
|   |   |-- checksums
|   |   |   |-- checksums.lock
|   |   |   `-- sha1-checksums.bin
|   |   |-- expanded
|   |   |-- fileChanges
|   |   |   `-- last-build.bin
|   |   |-- fileHashes
|   |   |   |-- fileHashes.bin
|   |   |   `-- fileHashes.lock
|   |   |-- gc.properties
|   |   `-- vcsMetadata
|   |-- buildOutputCleanup
|   |   |-- buildOutputCleanup.lock
|   |   `-- cache.properties
|   `-- vcs-1
|       `-- gc.properties
|-- Dockerfile
|-- build
|   |-- classes
|   |   `-- java
|   |       |-- main
|   |       `-- test
|   |-- reports
|   |   `-- problems
|   |       `-- problems-report.html
|   `-- resources
|       |-- main
|       `-- test
|-- build.gradle
|-- config
|   `-- checkstyle
|       `-- checkstyle.xml
|-- gradle
|   `-- wrapper
|       |-- gradle-wrapper.jar
|       `-- gradle-wrapper.properties
|-- gradlew
|-- gradlew.bat
|-- settings.gradle
`-- src
    |-- main
    |   |-- java
    |   |   `-- com
    |   |       `-- ssafy
    |   |           `-- codefarm
    |   |               |-- CodefarmApplication.java
    |   |               |-- card
    |   |               |   |-- controller
    |   |               |   |   `-- CardController.java
    |   |               |   |-- dto
    |   |               |   |   |-- query
    |   |               |   |   |   |-- CardDetailQueryDto.java
    |   |               |   |   |   `-- MyCardQueryDto.java
    |   |               |   |   `-- response
    |   |               |   |       |-- AllCollectionMasterDto.java
    |   |               |   |       |-- CardDetailResponseDto.java
    |   |               |   |       |-- CardRankingResponseDto.java
    |   |               |   |       |-- CardResponseDto.java
    |   |               |   |       |-- CardSummaryResponseDto.java
    |   |               |   |       |-- DrawCardResponseDto.java
    |   |               |   |       |-- MyCardListResponseDto.java
    |   |               |   |       |-- MyCardResponseDto.java
    |   |               |   |       |-- MyCardStatusResponseDto.java
    |   |               |   |       |-- TodayRareCollectorDto.java
    |   |               |   |       `-- TopCollectorDto.java
    |   |               |   |-- entity
    |   |               |   |   |-- Card.java
    |   |               |   |   |-- CardGrade.java
    |   |               |   |   `-- UserCard.java
    |   |               |   |-- repository
    |   |               |   |   |-- CardRepository.java
    |   |               |   |   |-- UserCardRepository.java
    |   |               |   |   `-- query
    |   |               |   |       |-- CardQueryRepository.java
    |   |               |   |       `-- CardQueryRepositoryImpl.java
    |   |               |   `-- service
    |   |               |       `-- CardService.java
    |   |               |-- common
    |   |               |   |-- authority
    |   |               |   |   |-- JwtAuthenticationTokenFilter.java
    |   |               |   |   |-- JwtTokenProvider.java
    |   |               |   |   `-- TokenInfo.java
    |   |               |   |-- config
    |   |               |   |   |-- HttpClientConfig.java
    |   |               |   |   |-- JacksonConfig.java
    |   |               |   |   |-- QuerydslConfig.java
    |   |               |   |   |-- SchedulerConfig.java
    |   |               |   |   `-- SecurityConfig.java
    |   |               |   |-- dto
    |   |               |   |   |-- CustomUserDetails.java
    |   |               |   |   |-- ErrorResponse.java
    |   |               |   |   |-- LoginTokenResult.java
    |   |               |   |   `-- SuccessResponse.java
    |   |               |   |-- exception
    |   |               |   |   |-- CustomException.java
    |   |               |   |   |-- CustomExceptionHandler.java
    |   |               |   |   `-- ErrorCode.java
    |   |               |   `-- service
    |   |               |       `-- CustomUserDetailsService.java
    |   |               |-- curriculum
    |   |               |   |-- controller
    |   |               |   |   `-- CurriculumController.java
    |   |               |   |-- dto
    |   |               |   |   |-- query
    |   |               |   |   |   |-- CurriculumDetailQueryDto.java
    |   |               |   |   |   |-- CurriculumProblemDetailQueryDto.java
    |   |               |   |   |   `-- CurriculumProblemOrderDto.java
    |   |               |   |   `-- response
    |   |               |   |       |-- CurriculumDetailResponseDto.java
    |   |               |   |       |-- CurriculumListItemResponseDto.java
    |   |               |   |       |-- CurriculumListResponseDto.java
    |   |               |   |       |-- CurriculumProblemItemResponseDto.java
    |   |               |   |       |-- CurriculumRecommendResponseDto.java
    |   |               |   |       `-- CurriculumResponseDto.java
    |   |               |   |-- entity
    |   |               |   |   |-- Curriculum.java
    |   |               |   |   |-- CurriculumDifficulty.java
    |   |               |   |   `-- CurriculumProblem.java
    |   |               |   |-- repository
    |   |               |   |   |-- CurriculumProblemRepository.java
    |   |               |   |   |-- CurriculumQueryRepository.java
    |   |               |   |   |-- CurriculumRepository.java
    |   |               |   |   `-- impl
    |   |               |   |       `-- CurriculumQueryRepositoryImpl.java
    |   |               |   `-- service
    |   |               |       `-- CurriculumService.java
    |   |               |-- hint
    |   |               |   |-- controller
    |   |               |   |   `-- HintController.java
    |   |               |   |-- dto
    |   |               |   |   |-- ai
    |   |               |   |   |   |-- AIHintRequest.java
    |   |               |   |   |   `-- AIHintResponse.java
    |   |               |   |   |-- requset
    |   |               |   |   |   `-- ManualHintRequestDto.java
    |   |               |   |   `-- response
    |   |               |   |       |-- HintItemResponseDto.java
    |   |               |   |       |-- HintListResponseDto.java
    |   |               |   |       `-- ManualHintResponseDto.java
    |   |               |   |-- entity
    |   |               |   |   |-- Hint.java
    |   |               |   |   `-- HintType.java
    |   |               |   |-- repository
    |   |               |   |   |-- HintRepository.java
    |   |               |   |   `-- SseEmitterRepository.java
    |   |               |   `-- service
    |   |               |       |-- AIHintServerClient.java
    |   |               |       |-- AutoHintSchedulerService.java
    |   |               |       |-- HintProcessingService.java
    |   |               |       `-- HintService.java
    |   |               |-- problem
    |   |               |   |-- controller
    |   |               |   |   `-- ProblemController.java
    |   |               |   |-- dto
    |   |               |   |   |-- query
    |   |               |   |   |   `-- ProblemListQueryDto.java
    |   |               |   |   `-- response
    |   |               |   |       |-- ProblemDetailResponseDto.java
    |   |               |   |       |-- ProblemListItemResponseDto.java
    |   |               |   |       |-- ProblemListResponseDto.java
    |   |               |   |       |-- ProblemResponseDto.java
    |   |               |   |       |-- ProblemStatisticsDto.java
    |   |               |   |       `-- ProblemUserStatusDto.java
    |   |               |   |-- entity
    |   |               |   |   |-- AlgorithmType.java
    |   |               |   |   |-- Problem.java
    |   |               |   |   |-- ProblemDifficulty.java
    |   |               |   |   `-- ProblemType.java
    |   |               |   |-- repository
    |   |               |   |   |-- ProblemQueryRepository.java
    |   |               |   |   |-- ProblemRepository.java
    |   |               |   |   `-- impl
    |   |               |   |       `-- ProblemQueryRepositoryImpl.java
    |   |               |   `-- service
    |   |               |       `-- ProblemService.java
    |   |               |-- result
    |   |               |   |-- controller
    |   |               |   |   `-- ResultController.java
    |   |               |   |-- dto
    |   |               |   |   |-- query
    |   |               |   |   |   `-- ReportDetailQueryDto.java
    |   |               |   |   |-- requset
    |   |               |   |   |   `-- SaveCodeSnapshotRequestDto.java
    |   |               |   |   `-- response
    |   |               |   |       |-- ProblemSimpleDto.java
    |   |               |   |       |-- ReportDetailResponseDto.java
    |   |               |   |       |-- ResultLearningDto.java
    |   |               |   |       |-- ResultMyReportListResponseDto.java
    |   |               |   |       `-- SaveCodeSnapshotResponseDto.java
    |   |               |   |-- entity
    |   |               |   |   |-- Language.java
    |   |               |   |   |-- Result.java
    |   |               |   |   `-- ResultType.java
    |   |               |   |-- repository
    |   |               |   |   |-- ResultQueryRepository.java
    |   |               |   |   |-- ResultRepository.java
    |   |               |   |   `-- impl
    |   |               |   |       `-- ResultQueryRepositoryImpl.java
    |   |               |   `-- service
    |   |               |       `-- ResultService.java
    |   |               |-- session
    |   |               |   |-- controller
    |   |               |   |   `-- SessionController.java
    |   |               |   |-- dto
    |   |               |   |   |-- execution
    |   |               |   |   |   |-- EvaluationContext.java
    |   |               |   |   |   |-- ExecuteServerRequest.java
    |   |               |   |   |   |-- ExecuteServerResult.java
    |   |               |   |   |   |-- SubmissionContext.java
    |   |               |   |   |   |-- SubmitContext.java
    |   |               |   |   |   `-- SubmitOutcome.java
    |   |               |   |   |-- feedback
    |   |               |   |   |   |-- FeedbackRequest.java
    |   |               |   |   |   `-- FeedbackResponse.java
    |   |               |   |   |-- redis
    |   |               |   |   |   |-- CodeSnapshotRedisDto.java
    |   |               |   |   |   `-- PreviousJudgementRedisDto.java
    |   |               |   |   |-- request
    |   |               |   |   |   |-- CreateSessionRequestDto.java
    |   |               |   |   |   |-- GiveUpSessionRequestDto.java
    |   |               |   |   |   |-- RunSessionRequestDto.java
    |   |               |   |   |   `-- SubmitSessionRequestDto.java
    |   |               |   |   `-- response
    |   |               |   |       |-- GiveUpSessionResponseDto.java
    |   |               |   |       |-- LatestCodeResponseDto.java
    |   |               |   |       |-- RunSessionResponseDto.java
    |   |               |   |       |-- SessionResponseDto.java
    |   |               |   |       |-- SessionResultItemResponseDto.java
    |   |               |   |       |-- SessionResultsResponseDto.java
    |   |               |   |       `-- SubmitSessionResponseDto.java
    |   |               |   |-- entity
    |   |               |   |   |-- Session.java
    |   |               |   |   `-- SessionStatus.java
    |   |               |   |-- repository
    |   |               |   |   `-- SessionRepository.java
    |   |               |   `-- service
    |   |               |       |-- ExecutionServerClient.java
    |   |               |       |-- FeedbackServerClient.java
    |   |               |       |-- SessionCodeRedisService.java
    |   |               |       `-- SessionService.java
    |   |               `-- user
    |   |                   |-- controller
    |   |                   |   `-- UserController.java
    |   |                   |-- dto
    |   |                   |   |-- request
    |   |                   |   |   |-- CheckEmailRequestDto.java
    |   |                   |   |   |-- CheckNicknameRequestDto.java
    |   |                   |   |   |-- LoginRequestDto.java
    |   |                   |   |   |-- UpdateUserProfileRequestDto.java
    |   |                   |   |   `-- UserSignupRequestDto.java
    |   |                   |   `-- response
    |   |                   |       |-- CheckEmailResponseDto.java
    |   |                   |       |-- CheckNicknameResponseDto.java
    |   |                   |       |-- LoginResponseDto.java
    |   |                   |       |-- TokenResponseDto.java
    |   |                   |       `-- UserResponseDto.java
    |   |                   |-- entity
    |   |                   |   `-- User.java
    |   |                   |-- repository
    |   |                   |   `-- UserRepository.java
    |   |                   `-- service
    |   |                       |-- RefreshTokenRedisService.java
    |   |                       `-- UserService.java
    |   `-- resources
    |       |-- application-dev.yml
    |       |-- application-prod.yml
    |       |-- application.yml
    |       `-- application.yml.bak
    `-- test
        `-- java
            `-- com
                `-- ssafy
                    `-- codefarm
                        `-- CodefarmApplicationTests.java
```

</details>
<details>
  <summary>
    exec
  </summary>

```
./exec
|-- dump-codefarm-202602091021.sql
|-- porting_manual.md
`-- scenario.md
```

</details>
<details>
  <summary>
    execution
  </summary>

```
./execution
|-- Dockerfile
|-- app
|   |-- __init__.py
|   |-- app.py
|   |-- models.py
|   `-- runner.py
|-- runner
|   `-- python
|       `-- Dockerfile
`-- scenario.md
```

</details>
<details>
  <summary>
    feedback
  </summary>

```
./feedback
|-- .gitignore
|-- Dockerfile
|-- app
|   |-- __init__.py
|   |-- __pycache__
|   |   `-- __init__.cpython-311.pyc
|   |-- app.py
|   `-- models.py
`-- requirements.txt
```

</details>
<details>
  <summary>
    frontend
  </summary>

```
./frontend
|-- .gitignore
|-- .prettierrc
|-- .vscode
|   `-- extensions.json
|-- README.md
|-- cursor
|   `-- mcp.json
|-- index.html
|-- jsconfig.json
|-- package-lock.json
|-- package.json
|-- public
|   `-- favicon.ico
|-- src
|   |-- App.vue
|   |-- api
|   |   |-- auth.js
|   |   |-- card.js
|   |   |-- hint.js
|   |   |-- index.js
|   |   |-- problem.js
|   |   |-- profile.js
|   |   |-- reports.js
|   |   `-- session.js
|   |-- assets
|   |   |-- banner
|   |   |   `-- rank.png
|   |   |-- card
|   |   |   |-- Gacha.png
|   |   |   `-- cardlist.png
|   |   |-- common
|   |   |   |-- logo.png
|   |   |   |-- patterns
|   |   |   |   |-- brick-wall.svg
|   |   |   |   `-- dot-pattern.svg
|   |   |   `-- style.css
|   |   `-- roadmap
|   |       |-- Roadmap.png
|   |       |-- chicken.png
|   |       |-- cowshed.png
|   |       |-- duck.png
|   |       |-- farmer.png
|   |       |-- forest.png
|   |       |-- fruits.png
|   |       |-- megacrew.png
|   |       |-- pond.png
|   |       |-- veg_field.png
|   |       `-- wood_panel_1.png
|   |-- components
|   |   |-- atoms
|   |   |   |-- AppToast.vue
|   |   |   |-- BellIcon.vue
|   |   |   |-- CarrotIcon.vue
|   |   |   |-- EscapeIcon.vue
|   |   |   |-- MarkdownText.vue
|   |   |   |-- PageShell.vue
|   |   |   `-- PageTitle.vue
|   |   |-- layout
|   |   |   `-- DefaultLayout.vue
|   |   `-- organisms
|   |       |-- CardDetail.vue
|   |       |-- CommonFooter.vue
|   |       |-- CommonHeader.vue
|   |       |-- ConfirmModal.vue
|   |       |-- HintModal.vue
|   |       |-- HintPanel.vue
|   |       |-- MainHeroBanner.vue
|   |       |-- MonacoEditor.vue
|   |       |-- NotebookFlip.vue
|   |       |-- ProblemCard.vue
|   |       |-- ProblemPanel.vue
|   |       |-- ProfileEditModal.vue
|   |       |-- ReportModal.vue
|   |       |-- RoadmapMap.vue
|   |       |-- SignupForm.vue
|   |       `-- TerminalPanel.vue
|   |-- composables
|   |   `-- useSSE.js
|   |-- main.js
|   |-- mocks
|   |   `-- sampled_30_clean.json
|   |-- router
|   |   `-- index.js
|   |-- stores
|   |   |-- auth.js
|   |   |-- card.js
|   |   |-- ide.js
|   |   |-- problem.js
|   |   |-- profile.js
|   |   |-- toast.js
|   |   `-- ui.js
|   |-- utils
|   |   `-- algorithm.js
|   `-- views
|       |-- CardView.vue
|       |-- IdeView.vue
|       |-- LoginView.vue
|       |-- MainView.vue
|       |-- ProblemView.vue
|       |-- ProfileView.vue
|       `-- RoadmapView.vue
|-- tailwind.config.js
`-- vite.config.js
```

</details>
<details>
  <summary>
    inference
  </summary>

```
./inference
|-- READMD.md
|-- __pycache__
|   `-- app.cpython-311.pyc
|-- app.py
|-- models
|   |-- __pycache__
|   |   |-- model1.cpython-311.pyc
|   |   `-- model2.cpython-311.pyc
|   |-- model1.py
|   `-- model2.py
|-- requirements.txt
`-- utils
    |-- __pycache__
    |   |-- auth.cpython-311.pyc
    |   |-- json_utils.cpython-311.pyc
    |   |-- prompt.cpython-311.pyc
    |   `-- prompt_builder.cpython-311.pyc
    |-- auth.py
    |-- constant.py
    |-- json_utils.py
    |-- labels.py
    |-- prompt.py
    `-- prompt_builder.py
```

</details>
<details>
  <summary>
    infra
  </summary>

```
./infra
|-- README.md
|-- branch_strategy.md
`-- nginx
    |-- Dockerfile
    `-- conf.d
        `-- default.conf
```

</details>
.gitlab-ci.yml

### EC2

<details>
  <summary>
    /srv/app
  </summary>

```
./srv/app
├── .current_image_tag_dev
├── .current_image_tag_foundation
├── .current_image_tag_prod
├── .env
├── .previous_image_tag_dev
├── .previous_image_tag_foundation
├── .previous_image_tag_prod
├── docker
│   └── runner
│       └── python
│           └── Dockerfile
├── docker-compose.db.yml
├── docker-compose.dev.yml
├── docker-compose.exec.yml
├── docker-compose.feedback.yml
├── docker-compose.prod.yml
├── letsencrypt-webroot
└── scripts
    ├── deploy_foundation.sh
    ├── deploy_server.sh
    ├── healthcheck.sh
    └── rollback.sh
```

</details>

### Elice GPU Server

<details>
  <summary>
    /srv/app
  </summary>

```
./srv/app
└── app
    ├── builds
    │   └── _A_GMOZgw
    │       └── 0
    │           └── s14-webmobile2-sub1
    │               ├── S14P11B109
    │               │   └── repo
    │               │       ├── .env.development
    │               │       ├── .git
    │               │       │   ├── branches
    │               │       │   ├── config
    │               │       │   ├── config.worktree
    │               │       │   ├── description
    │               │       │   ├── FETCH_HEAD
    │               │       │   ├── HEAD
    │               │       │   ├── hooks
    │               │       │   │   ├── applypatch-msg.sample
    │               │       │   │   ├── commit-msg.sample
    │               │       │   │   ├── fsmonitor-watchman.sample
    │               │       │   │   ├── post-update.sample
    │               │       │   │   ├── pre-applypatch.sample
    │               │       │   │   ├── pre-commit.sample
    │               │       │   │   ├── pre-merge-commit.sample
    │               │       │   │   ├── prepare-commit-msg.sample
    │               │       │   │   ├── pre-push.sample
    │               │       │   │   ├── pre-rebase.sample
    │               │       │   │   ├── pre-receive.sample
    │               │       │   │   ├── push-to-checkout.sample
    │               │       │   │   └── update.sample
    │               │       │   ├── index
    │               │       │   ├── info
    │               │       │   │   ├── exclude
    │               │       │   │   └── sparse-checkout
    │               │       │   ├── logs
    │               │       │   │   └── HEAD
    │               │       │   ├── objects
    │               │       │   │   ├── info
    │               │       │   │   └── pack
    │               │       │   │       ├── pack-e577346f3568c2ded93a3f7cad1048b5504be39f.idx
    │               │       │   │       └── pack-e577346f3568c2ded93a3f7cad1048b5504be39f.pack
    │               │       │   ├── refs
    │               │       │   │   ├── heads
    │               │       │   │   └── tags
    │               │       │   └── shallow
    │               │       ├── .gitignore
    │               │       ├── .gitlab-ci.yml
    │               │       ├── inference
    │               │       │   ├── app.py
    │               │       │   ├── models
    │               │       │   │   ├── model1.py
    │               │       │   │   ├── model2.py
    │               │       │   │   └── __pycache__
    │               │       │   │       ├── model1.cpython-311.pyc
    │               │       │   │       └── model2.cpython-311.pyc
    │               │       │   ├── __pycache__
    │               │       │   │   └── app.cpython-311.pyc
    │               │       │   ├── READMD.md
    │               │       │   ├── requirements.txt
    │               │       │   └── utils
    │               │       │       ├── auth.py
    │               │       │       ├── constant.py
    │               │       │       ├── json_utils.py
    │               │       │       ├── labels.py
    │               │       │       ├── prompt_builder.py
    │               │       │       ├── prompt.py
    │               │       │       └── __pycache__
    │               │       │           ├── auth.cpython-311.pyc
    │               │       │           ├── json_utils.cpython-311.pyc
    │               │       │           ├── prompt_builder.cpython-311.pyc
    │               │       │           └── prompt.cpython-311.pyc
    │               │       ├── package-lock.json
    │               │       └── README.md
    │               └── S14P11B109.tmp
    ├── .env
    └── inference
        ├── app.py
        ├── builds
        │   └── _A_GMOZgw
        │       └── 0
        │           └── s14-webmobile2-sub1
        │               ├── S14P11B109
        │               │   └── repo
        │               │       ├── .env.development
        │               │       ├── .git
        │               │       │   ├── branches
        │               │       │   ├── config
        │               │       │   ├── config.worktree
        │               │       │   ├── description
        │               │       │   ├── FETCH_HEAD
        │               │       │   ├── HEAD
        │               │       │   ├── hooks
        │               │       │   │   ├── applypatch-msg.sample
        │               │       │   │   ├── commit-msg.sample
        │               │       │   │   ├── fsmonitor-watchman.sample
        │               │       │   │   ├── post-update.sample
        │               │       │   │   ├── pre-applypatch.sample
        │               │       │   │   ├── pre-commit.sample
        │               │       │   │   ├── pre-merge-commit.sample
        │               │       │   │   ├── prepare-commit-msg.sample
        │               │       │   │   ├── pre-push.sample
        │               │       │   │   ├── pre-rebase.sample
        │               │       │   │   ├── pre-receive.sample
        │               │       │   │   ├── push-to-checkout.sample
        │               │       │   │   └── update.sample
        │               │       │   ├── index
        │               │       │   ├── info
        │               │       │   │   ├── exclude
        │               │       │   │   └── sparse-checkout
        │               │       │   ├── logs
        │               │       │   │   └── HEAD
        │               │       │   ├── objects
        │               │       │   │   ├── info
        │               │       │   │   └── pack
        │               │       │   │       ├── pack-b2c13af21cd5076c5fe9c2f6e26bb4c1f7c6464e.idx
        │               │       │   │       └── pack-b2c13af21cd5076c5fe9c2f6e26bb4c1f7c6464e.pack
        │               │       │   ├── refs
        │               │       │   │   ├── heads
        │               │       │   │   └── tags
        │               │       │   └── shallow
        │               │       ├── .gitignore
        │               │       ├── .gitlab-ci.yml
        │               │       ├── inference
        │               │       │   ├── app.py
        │               │       │   ├── models
        │               │       │   │   ├── model1.py
        │               │       │   │   ├── model2.py
        │               │       │   │   └── __pycache__
        │               │       │   │       ├── model1.cpython-311.pyc
        │               │       │   │       └── model2.cpython-311.pyc
        │               │       │   ├── __pycache__
        │               │       │   │   └── app.cpython-311.pyc
        │               │       │   ├── READMD.md
        │               │       │   ├── requirements.txt
        │               │       │   └── utils
        │               │       │       ├── auth.py
        │               │       │       ├── constant.py
        │               │       │       ├── json_utils.py
        │               │       │       ├── labels.py
        │               │       │       ├── prompt_builder.py
        │               │       │       ├── prompt.py
        │               │       │       └── __pycache__
        │               │       │           ├── auth.cpython-311.pyc
        │               │       │           ├── json_utils.cpython-311.pyc
        │               │       │           ├── prompt_builder.cpython-311.pyc
        │               │       │           └── prompt.cpython-311.pyc
        │               │       ├── package-lock.json
        │               │       └── README.md
        │               └── S14P11B109.tmp
        ├── models
        │   ├── label_model
        │   │   ├── chat_template.jinja
        │   │   ├── config.json
        │   │   ├── model.safetensors
        │   │   ├── special_tokens_map.json
        │   │   ├── tokenizer_config.json
        │   │   ├── tokenizer.json
        │   │   └── tokenizer.model
        │   ├── model1.py
        │   ├── model2.py
        │   ├── __pycache__
        │   │   ├── model1.cpython-311.pyc
        │   │   └── model2.cpython-311.pyc
        │   └── text_model
        │       ├── fold_1
        │       │   ├── adapter_config.json
        │       │   ├── adapter_model.safetensors
        │       │   ├── chat_template.jinja
        │       │   ├── README.md
        │       │   ├── special_tokens_map.json
        │       │   ├── tokenizer_config.json
        │       │   └── tokenizer.json
        │       ├── fold_2
        │       │   ├── adapter_config.json
        │       │   ├── adapter_model.safetensors
        │       │   ├── chat_template.jinja
        │       │   ├── README.md
        │       │   ├── special_tokens_map.json
        │       │   ├── tokenizer_config.json
        │       │   └── tokenizer.json
        │       ├── fold_3
        │       │   ├── adapter_config.json
        │       │   ├── adapter_model.safetensors
        │       │   ├── chat_template.jinja
        │       │   ├── README.md
        │       │   ├── special_tokens_map.json
        │       │   ├── tokenizer_config.json
        │       │   └── tokenizer.json
        │       ├── fold_4
        │       │   ├── adapter_config.json
        │       │   ├── adapter_model.safetensors
        │       │   ├── chat_template.jinja
        │       │   ├── README.md
        │       │   ├── special_tokens_map.json
        │       │   ├── tokenizer_config.json
        │       │   └── tokenizer.json
        │       └── fold_5
        │           ├── adapter_config.json
        │           ├── adapter_model.safetensors
        │           ├── chat_template.jinja
        │           ├── README.md
        │           ├── special_tokens_map.json
        │           ├── tokenizer_config.json
        │           └── tokenizer.json
        ├── __pycache__
        │   └── app.cpython-311.pyc
        ├── READMD.md
        ├── requirements.txt
        └── utils
            ├── auth.py
            ├── constant.py
            ├── json_utils.py
            ├── labels.py
            ├── prompt_builder.py
            ├── prompt.py
            └── __pycache__
                ├── auth.cpython-311.pyc
                ├── constant.cpython-311.pyc
                ├── json_utils.cpython-311.pyc
                ├── labels.cpython-311.pyc
                ├── prompt_builder.cpython-311.pyc
                └── prompt.cpython-311.pyc
```

</details>

## 📦 프로젝트 산출물

### 🖼️ 화면 설계서
![codefarm_wireframe](./assets/wireframe.png)

### 🗄️ ERD

![codefarm_erd](./assets/codefarm%20erd.png)

### 🗓️ Jira Issues
