package com.ssafy.codefarm.session.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.hint.service.AutoHintSchedulerService;
import com.ssafy.codefarm.hint.service.HintService;
import com.ssafy.codefarm.problem.entity.Problem;
import com.ssafy.codefarm.problem.repository.ProblemRepository;
import com.ssafy.codefarm.result.dto.requset.SaveCodeSnapshotRequestDto;
import com.ssafy.codefarm.result.dto.response.SaveCodeSnapshotResponseDto;
import com.ssafy.codefarm.result.entity.Result;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.result.repository.ResultRepository;
import com.ssafy.codefarm.session.dto.execution.*;
import com.ssafy.codefarm.session.dto.feedback.FeedbackRequest;
import com.ssafy.codefarm.session.dto.redis.CodeSnapshotRedisDto;
import com.ssafy.codefarm.session.dto.request.CreateSessionRequestDto;
import com.ssafy.codefarm.session.dto.request.GiveUpSessionRequestDto;
import com.ssafy.codefarm.session.dto.request.RunSessionRequestDto;
import com.ssafy.codefarm.session.dto.request.SubmitSessionRequestDto;
import com.ssafy.codefarm.session.dto.response.*;
import com.ssafy.codefarm.session.entity.Session;
import com.ssafy.codefarm.session.entity.SessionStatus;
import com.ssafy.codefarm.session.repository.SessionRepository;
import com.ssafy.codefarm.user.entity.User;
import com.ssafy.codefarm.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;
import org.springframework.transaction.support.TransactionTemplate;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class SessionService {

    private final ExecutionServerClient executionServerClient;
    private final SessionCodeRedisService sessionCodeRedisService;
    private final FeedbackServerClient feedbackServerClient;
    private final AutoHintSchedulerService autoHintSchedulerService;
    private final HintService hintService;

    private final SessionRepository sessionRepository;
    private final UserRepository userRepository;
    private final ProblemRepository problemRepository;
    private final ResultRepository resultRepository;

    private final TransactionTemplate transactionTemplate;

    public SessionResponseDto createSession(Long userId, CreateSessionRequestDto createSessionRequestDto) {

        if (sessionRepository.existsByUserIdAndStatus(userId, SessionStatus.ACTIVE)) {
            throw new CustomException("이미 진행 중인 세션이 존재합니다.", ErrorCode.DUPLICATE_RESOURCE);
        }

        User user = userRepository.getReferenceById(userId);

        Problem problem = problemRepository.findById(createSessionRequestDto.getProblemId())
                .orElseThrow(() ->
                        new CustomException("문제를 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND)
        );

        Session session = Session.builder()
                .status(SessionStatus.ACTIVE)
                .startedAt(LocalDateTime.now())
                .user(user)
                .problem(problem)
                .build();

        try {
            sessionRepository.save(session);
        } catch (DataIntegrityViolationException e) {
            throw new CustomException(
                    "이미 진행 중인 세션이 존재합니다.",
                    ErrorCode.DUPLICATE_RESOURCE
            );
        }

        sessionCodeRedisService.initialize(session.getId());

        if (TransactionSynchronizationManager.isSynchronizationActive()) {
            TransactionSynchronizationManager.registerSynchronization(
                    new TransactionSynchronization() {
                        @Override
                        public void afterCommit() {
                            autoHintSchedulerService.start(session.getId());
                        }
                    }
            );
        } else {
            autoHintSchedulerService.start(session.getId());
        }

        return SessionResponseDto.from(session);
    }

    public SessionResponseDto closeSession(Long userId, Long sessionId) {
        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        if (session.getStatus() == SessionStatus.CLOSED) {
            throw new CustomException("이미 종료된 세션입니다.", ErrorCode.BAD_REQUEST);
        }

        session.close();

        sessionCodeRedisService.delete(sessionId);

        autoHintSchedulerService.stop(sessionId);
        hintService.clearSession(sessionId);

        return SessionResponseDto.from(session);
    }

    @Transactional(readOnly = true)
    public SessionResponseDto getSessionDetail(Long userId, Long sessionId) {
        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() ->
                        new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        return SessionResponseDto.from(session);
    }

    @Transactional(readOnly = true)
    public SessionResponseDto getActiveSession(Long userId) {
        return sessionRepository.findByUserIdAndStatus(userId, SessionStatus.ACTIVE)
                .map(SessionResponseDto::from)
                .orElse(null);
    }

    public SaveCodeSnapshotResponseDto saveCodeSnapshot(Long userId, Long sessionId, SaveCodeSnapshotRequestDto saveCodeSnapshotRequestDto) {
        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        if (session.getStatus() != SessionStatus.ACTIVE) {
            throw new CustomException("종료된 세션에는 코드를 저장할 수 없습니다.", ErrorCode.BAD_REQUEST);
        }

        LocalDateTime now = LocalDateTime.now();

        CodeSnapshotRedisDto snapshot = CodeSnapshotRedisDto.builder()
                .language(saveCodeSnapshotRequestDto.getLanguage())
                .code(saveCodeSnapshotRequestDto.getCode())
                .savedAt(now)
                .build();

        sessionCodeRedisService.appendSnapshot(sessionId, snapshot);

        return SaveCodeSnapshotResponseDto.from(now);

    }

    @Transactional(readOnly = true)
    public LatestCodeResponseDto getLatestCode(Long userId, Long sessionId) {
        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() ->
                        new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        if (session.getStatus() != SessionStatus.ACTIVE) {
            throw new CustomException("종료된 세션에는 코드를 저장할 수 없습니다.", ErrorCode.BAD_REQUEST);
        }

        CodeSnapshotRedisDto snapshot = sessionCodeRedisService.getLatestSnapshot(sessionId);

        if (snapshot == null) {
            throw new CustomException("저장된 코드가 존재하지 않습니다.", ErrorCode.RESOURCE_NOT_FOUND);
        }

        return LatestCodeResponseDto.from(snapshot.getCode(), snapshot.getLanguage(), snapshot.getSavedAt());
    }

    public RunSessionResponseDto runSession(Long sessionId, Long userId, RunSessionRequestDto requestDto) {

        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() ->
                        new CustomException("세션이 존재하지 않습니다.", ErrorCode.RESOURCE_NOT_FOUND)
                );

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        if (session.getStatus() != SessionStatus.ACTIVE) {
            throw new CustomException("종료된 세션에는 코드를 실행할 수 없습니다.", ErrorCode.BAD_REQUEST);
        }

        // Execution 서버 호출 DTO 생성
        ExecuteServerRequest executionRequestDto =
                new ExecuteServerRequest(
                        requestDto.getLanguage(),
                        requestDto.getCode(),
                        requestDto.getInput() == null ? "" : requestDto.getInput(),
                        2000,
                        128,
                        0.5
                );

        // 외부 서버 호출 (동기)
        ExecuteServerResult result = executionServerClient.execute(executionRequestDto);

        return RunSessionResponseDto.from(
                result.stdout(),
                result.stderr(),
                result.memoryUsage(),
                result.execTime(),
                result.isTimeout(),
                result.isOom()
        );
    }

    public SubmitSessionResponseDto submitSession(
            Long userId,
            Long sessionId,
            SubmitSessionRequestDto submitSessionRequestDto
    ) {

        SubmitContext ctx = loadSubmitContext(userId, sessionId);

        ExecuteServerRequest executionRequest =
                new ExecuteServerRequest(
                        submitSessionRequestDto.getLanguage(),
                        submitSessionRequestDto.getCode(),
                        ctx.problem().getTestcasesInput(),
                        ctx.problem().getTimeLimit() * 1000,
                        ctx.problem().getMemoryLimit(),
                        0.5
                );

        ExecuteServerResult exec = executionServerClient.execute(executionRequest);

        return saveSubmitResult(ctx, submitSessionRequestDto, exec);
    }

    private SubmitSessionResponseDto saveSubmitResult(
            SubmitContext submitContext,
            SubmitSessionRequestDto submitSessionRequestDto,
            ExecuteServerResult executeServerResult
    ) {
        return transactionTemplate.execute(status -> {

            SubmitOutcome submitOutcome =
                    SubmitOutcome.from(submitContext, executeServerResult);

            ResultType resultType = decideResultType(submitOutcome);

            Integer memory = toIntegerSafely(executeServerResult.memoryUsage());

            Result result = Result.builder()
                    .session(submitContext.session())
                    .resultType(resultType)
                    .language(submitSessionRequestDto.getLanguage())
                    .code(submitSessionRequestDto.getCode())
                    .solveTime(submitContext.solveTime())
                    .execTime(executeServerResult.execTime())
                    .memory(memory)
                    .feedback(null)
                    .build();

            boolean isFirstSolve = false;
            if (resultType == ResultType.SUCCESS) {
                if (!resultRepository.existsBySessionUserIdAndSessionProblemIdAndResultType(
                        submitContext.session().getUser().getId(),
                        submitContext.session().getProblem().getId(),
                        ResultType.SUCCESS
                )) {
                    isFirstSolve = true;
                }
            }

            resultRepository.save(result);

            if (isFirstSolve) {
                int basePoint = 0;
                Integer difficulty = submitContext.problem().getDifficulty();
                if (difficulty != null) {
                    switch (difficulty) {
                        case 1 -> basePoint = 30;
                        case 2 -> basePoint = 50;
                        case 3 -> basePoint = 80;
                        case 4 -> basePoint = 100;
                        case 5 -> basePoint = 150;
                    }
                }

                if (basePoint > 0) {
                    int usedHint = submitContext.session().getUsedHint();
                    int penalty = (int) (basePoint * 0.1 * usedHint);
                    int finalPoint = Math.max(0, basePoint - penalty);

                    submitContext.session().getUser().increasePoint(finalPoint);
                }
            }

            if (resultType == ResultType.FAIL) {
                return SubmitSessionResponseDto.fail(
                        EvaluationContext.from(submitOutcome)
                );
            }

            String feedback;
            try {
                // Redis에서 이전 판정 기록 조회
                List<FeedbackRequest.PreviousJudgement> previousJudgements =
                        FeedbackRequest.PreviousJudgement.fromList(
                                sessionCodeRedisService.getPreviousJudgements(submitContext.session().getId())
                        );

                // FeedbackRequest 생성 및 요청
                FeedbackRequest feedbackRequest =
                        FeedbackRequest.of(
                                result,
                                previousJudgements
                        );

                feedback = feedbackServerClient.requestFeedback(feedbackRequest);
            } catch (Exception e) {
                feedback = "정답입니다! 수고했어요.";
            }

            result.updateFeedback(feedback);

            submitContext.session().close();

            Long sessionId = submitContext.session().getId();

            if (TransactionSynchronizationManager.isSynchronizationActive()) {
                TransactionSynchronizationManager.registerSynchronization(
                        new TransactionSynchronization() {
                            @Override
                            public void afterCommit() {
                                sessionCodeRedisService.delete(sessionId);
                                log.info("Redis deleted after DB commit. sessionId={}", sessionId);
                                autoHintSchedulerService.stop(sessionId);
                                hintService.clearSession(sessionId);
                            }
                        }
                );
            } else {
                // 혹시 동기화가 활성화되지 않은 경우(거의 없음)
                sessionCodeRedisService.delete(sessionId);
                autoHintSchedulerService.stop(sessionId);
                hintService.clearSession(sessionId);
            }
            return SubmitSessionResponseDto.success(
                    SubmissionContext.from(result),
                    EvaluationContext.from(submitOutcome),
                    feedback
            );
        });
    }

    private ResultType decideResultType(SubmitOutcome outcome) {
        boolean success =
                outcome.totalCount() != null
                        && outcome.passedCount() != null
                        && outcome.totalCount().equals(outcome.passedCount())
                        && !Boolean.TRUE.equals(outcome.isTimeout())
                        && !Boolean.TRUE.equals(outcome.isOom())
                        && (outcome.stderr() == null || outcome.stderr().isBlank());

        return success ? ResultType.SUCCESS : ResultType.FAIL;
    }

    private String decideFeedback(ResultType resultType, SubmitOutcome outcome) {
        if (resultType == ResultType.SUCCESS) {
            return "반복문과 조건을 적절히 사용해 문제를 정확히 해결했어요. 다음에는 입력 처리 부분을 더 간결하게 작성해보세요.";
        }

        return outcome.failReason();
    }

    private Integer toIntegerSafely(Long value) { // 굳이 필요 없는데 그냥 안전장치
        if (value == null) {
            return null;
        }
        if (value > Integer.MAX_VALUE) {
            return Integer.MAX_VALUE;
        }
        if (value < Integer.MIN_VALUE) {
            return Integer.MIN_VALUE;
        }
        return value.intValue();
    }

    private SubmitContext loadSubmitContext(Long userId, Long sessionId) {
        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() ->
                        new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND)
                );

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        if (session.getStatus() != SessionStatus.ACTIVE) {
            throw new CustomException("종료된 세션에는 제출할 수 없습니다.", ErrorCode.BAD_REQUEST);
        }

        Problem problem = problemRepository.findById(session.getProblem().getId())
                .orElseThrow(() ->
                        new CustomException("문제를 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND)
                );

        if (problem.getTestcasesInput() == null || problem.getTestcasesInput().isBlank()) {
            throw new CustomException("테스트 입력이 존재하지 않습니다.", ErrorCode.INTERNAL_SERVER_ERROR);
        }

        if (problem.getTestcasesOutput() == null || problem.getTestcasesOutput().isBlank()) {
            throw new CustomException("테스트 출력이 존재하지 않습니다.", ErrorCode.INTERNAL_SERVER_ERROR);
        }

        int solveTime =
                (int) Duration.between(session.getStartedAt(), LocalDateTime.now()).toSeconds();

        return new SubmitContext(session, problem, solveTime);
    }

    public GiveUpSessionResponseDto giveUpSession(Long userId, Long sessionId, GiveUpSessionRequestDto requestDto) {

        SubmitContext ctx = loadSubmitContext(userId, sessionId);

        return transactionTemplate.execute(status -> {

            // 코드 결정 (우선순위: request → redis → "")
            String finalCode = requestDto.getCode();

            if (finalCode == null || finalCode.isBlank()) {
                CodeSnapshotRedisDto latest =
                        sessionCodeRedisService.getLatestSnapshot(sessionId);

                finalCode = latest != null ? latest.getCode() : "";
            }

            int solveTime =
                    (int) Duration.between(ctx.session().getStartedAt(), LocalDateTime.now()).toSeconds();

            Result result = Result.builder()
                    .session(ctx.session())
                    .resultType(ResultType.GIVE_UP)
                    .language(requestDto.getLanguage())
                    .code(finalCode)
                    .solveTime(solveTime)
                    .execTime(null)
                    .memory(null)
                    .feedback(null)
                    .build();

            resultRepository.save(result);

            String feedback;
            try {
                // Redis에서 이전 판정 기록 조회
                List<FeedbackRequest.PreviousJudgement> previousJudgements =
                       FeedbackRequest.PreviousJudgement.fromList(
                                sessionCodeRedisService.getPreviousJudgements(sessionId)
                        );

                // FeedbackRequest 생성 및 요청
                FeedbackRequest feedbackRequest =
                        FeedbackRequest.of(
                                result,
                                previousJudgements
                        );

                feedback = feedbackServerClient.requestFeedback(feedbackRequest);
            } catch (Exception e) {
                feedback = "이번 문제는 어려웠군요. 다음에는 힌트를 적극 활용해보세요!";
            }

            result.updateFeedback(feedback);

            ctx.session().close();

            Long sid = ctx.session().getId();

            TransactionSynchronizationManager.registerSynchronization(
                    new TransactionSynchronization() {
                        @Override
                        public void afterCommit() {
                            sessionCodeRedisService.delete(sid);
                            log.info("Redis deleted after GIVE_UP commit. sessionId={}", sid);
                            autoHintSchedulerService.stop(sid);
                            hintService.clearSession(sid);
                        }
                    }
            );

            return GiveUpSessionResponseDto.from(result);
        });
    }

    @Transactional(readOnly = true)
    public SessionResultsResponseDto getSessionResults(
            Long userId,
            Long sessionId
    ) {

        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() ->
                        new CustomException(
                                "세션을 찾을 수 없습니다.",
                                ErrorCode.RESOURCE_NOT_FOUND
                        )
                );

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException(
                    "해당 세션에 접근할 수 없습니다.",
                    ErrorCode.FORBIDDEN
            );
        }

        List<Result> results =
                resultRepository.findBySessionIdOrderByCreatedAtDesc(sessionId);

        List<SessionResultItemResponseDto> items =
                results.stream()
                        .map(SessionResultItemResponseDto::from)
                        .toList();

        return SessionResultsResponseDto.from(items);
    }
}
