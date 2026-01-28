package com.ssafy.codefarm.session.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.problem.entity.Problem;
import com.ssafy.codefarm.problem.repository.ProblemRepository;
import com.ssafy.codefarm.result.dto.requset.SaveCodeSnapshotRequestDto;
import com.ssafy.codefarm.result.dto.response.SaveCodeSnapshotResponseDto;
import com.ssafy.codefarm.result.entity.Result;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.result.repository.ResultRepository;
import com.ssafy.codefarm.session.dto.execution.ExecuteServerRequest;
import com.ssafy.codefarm.session.dto.execution.SubmitContext;
import com.ssafy.codefarm.session.dto.execution.SubmitOutcome;
import com.ssafy.codefarm.session.dto.redis.CodeSnapshotRedisDto;
import com.ssafy.codefarm.session.dto.request.CreateSessionRequestDto;
import com.ssafy.codefarm.session.dto.request.RunSessionRequestDto;
import com.ssafy.codefarm.session.dto.request.SubmitSessionRequestDto;
import com.ssafy.codefarm.session.dto.response.LatestCodeResponseDto;
import com.ssafy.codefarm.session.dto.response.RunSessionResponseDto;
import com.ssafy.codefarm.session.dto.response.SessionResponseDto;
import com.ssafy.codefarm.session.dto.response.SubmitSessionResponseDto;
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
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.time.Duration;
import java.time.LocalDateTime;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class SessionService {

    private final ExecutionServerClient executionServerClient;
    private final SessionCodeRedisService sessionCodeRedisService;

    private final SessionRepository sessionRepository;
    private final UserRepository userRepository;
    private final ProblemRepository problemRepository;
    private final ResultRepository resultRepository;


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
        Session session = sessionRepository.findByUserIdAndStatus(userId, SessionStatus.ACTIVE)
                .orElseThrow(() ->
                        new CustomException("활성 세션이 존재하지 않습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        return SessionResponseDto.from(session);
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

    public Mono<RunSessionResponseDto> runSession(Long sessionId, Long userId, RunSessionRequestDto requestDto) {

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
                        requestDto.getInput(),
                        2000,
                        128,
                        0.5
                );

        // 외부 서버 호출
        return executionServerClient.execute(executionRequestDto)
                .map(result ->
                        RunSessionResponseDto.from(
                                result.stdout(),
                                result.stderr(),
                                result.memoryUsage(),
                                result.execTime(),
                                result.isTimeout(),
                                result.isOom()
                        )
                );

    }

    public Mono<SubmitSessionResponseDto> submitSession(
            Long userId,
            Long sessionId,
            SubmitSessionRequestDto submitSessionRequestDto
    ) {

        return Mono.fromCallable(() -> loadSubmitContext(userId, sessionId))
                .subscribeOn(Schedulers.boundedElastic())
                .flatMap(ctx -> {

                    ExecuteServerRequest executionRequest =
                            new ExecuteServerRequest(
                                    submitSessionRequestDto.getLanguage(),
                                    submitSessionRequestDto.getCode(),
                                    ctx.problem().getTestcasesInput(),
                                    ctx.problem().getTimeLimit() * 1000,
                                    ctx.problem().getMemoryLimit(),
                                    0.5
                            );

                    return executionServerClient.execute(executionRequest)
                            .flatMap(exec ->
                                    Mono.fromCallable(() -> saveSubmitResult(ctx, submitSessionRequestDto, exec))
                                            .subscribeOn(Schedulers.boundedElastic())
                            );
                });
    }

    private SubmitSessionResponseDto saveSubmitResult(
            SubmitContext ctx,
            SubmitSessionRequestDto submitSessionRequestDto,
            com.ssafy.codefarm.session.dto.execution.ExecuteServerResult exec
    ) {

        SubmitOutcome outcome =
                SubmitOutcome.from(
                        ctx.problem().getTestcasesOutput(),
                        exec.stdout(),
                        exec.stderr(),
                        exec.isTimeout(),
                        exec.isOom()
                );

        ResultType resultType =
                decideResultType(outcome);

        String feedback =
                decideFeedback(resultType, outcome);

        Integer memory =
                toIntegerSafely(exec.memoryUsage());

        Result result = Result.builder()
                .session(ctx.session())
                .resultType(resultType)
                .language(submitSessionRequestDto.getLanguage())
                .code(submitSessionRequestDto.getCode())
                .solveTime(ctx.solveTime())
                .execTime(exec.execTime())
                .memory(memory)
                .feedback(feedback)
                .build();

        resultRepository.save(result);

        if (resultType == ResultType.SUCCESS) {
            ctx.session().close();
            sessionCodeRedisService.delete(ctx.session().getId());
        }

        return SubmitSessionResponseDto.from(result, outcome);
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

    private Integer toIntegerSafely(Long value) {
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
}
