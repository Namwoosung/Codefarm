package com.ssafy.codefarm.hint.service;

import com.ssafy.codefarm.hint.dto.ai.AIHintRequest;
import com.ssafy.codefarm.hint.dto.ai.AIHintResponse;
import com.ssafy.codefarm.hint.entity.Hint;
import com.ssafy.codefarm.hint.entity.HintType;
import com.ssafy.codefarm.hint.repository.HintRepository;
import com.ssafy.codefarm.session.dto.redis.CodeSnapshotRedisDto;
import com.ssafy.codefarm.session.dto.redis.PreviousJudgementRedisDto;
import com.ssafy.codefarm.session.entity.Session;
import com.ssafy.codefarm.session.entity.SessionStatus;
import com.ssafy.codefarm.session.repository.SessionRepository;
import com.ssafy.codefarm.session.service.SessionCodeRedisService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.TaskScheduler;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

@Slf4j
@Service
@RequiredArgsConstructor
public class AutoHintSchedulerService {

    private final TaskScheduler taskScheduler;
    private final AIHintServerClient aiHintServerClient;

    private final SessionRepository sessionRepository;
    private final SessionCodeRedisService sessionCodeRedisService;
    private final HintRepository hintRepository;
    private final HintService hintService;

    private final ConcurrentHashMap<Long, ScheduledFuture<?>> tasks = new ConcurrentHashMap<>();

    private static final Duration INTERVAL = Duration.ofMinutes(1); // test를 위해 1분으로 설정

    public void start(Long sessionId) {

        // 이미 실행 중이면 중복 시작 방지
        if (tasks.containsKey(sessionId)) {
            log.warn("Auto hint scheduler already running. sessionId={}", sessionId);
            return;
        }

        ScheduledFuture<?> future = taskScheduler.scheduleAtFixedRate(
                () -> process(sessionId),
                Instant.now().plus(INTERVAL),
                INTERVAL
        );

        ScheduledFuture<?> existing = tasks.putIfAbsent(sessionId, future);

        if (existing != null) {
            // 이미 다른 스레드가 먼저 등록했다면 방금 만든 future 취소
            future.cancel(true);
            log.warn("Auto hint scheduler duplicate prevented. sessionId={}", sessionId);
            return;
        }

        log.info("Auto hint scheduler started. sessionId={}", sessionId);
    }

    public void stop(Long sessionId) {
        ScheduledFuture<?> future = tasks.remove(sessionId);
        if (future != null) {
            future.cancel(true);
            log.info("Auto hint scheduler stopped. sessionId={}", sessionId);
        }
    }

    public void process(Long sessionId) {

        Session session = sessionRepository.findById(sessionId).orElse(null);

        if (session == null) {
            stop(sessionId);
            return;
        }

        // 세션 24시간 초과 여부 체크
        LocalDateTime now = LocalDateTime.now();
        if (session.getStatus() == SessionStatus.ACTIVE
                && session.getStartedAt() != null
                && Duration.between(session.getStartedAt(), now).toHours() >= 24) {

            log.warn("Session expired after 24 hours. sessionId={}", sessionId);

            session.close(); // DB 상태 변경

            // 리소스 정리
            sessionCodeRedisService.delete(sessionId);
            hintService.clearSession(sessionId);

            stop(sessionId);

            return;
        }

        if (session.getStatus() != SessionStatus.ACTIVE) {
            stop(sessionId);
            return;
        }


        // Redis 데이터 조회
        List<CodeSnapshotRedisDto> codeHistory =
                sessionCodeRedisService.getSnapshots(sessionId);

        List<PreviousJudgementRedisDto> previousJudgements =
                sessionCodeRedisService.getPreviousJudgements(sessionId);

        AIHintRequest request = AIHintRequest.of(
                session,
                session.getUser(),
                session.getProblem(),
                null,
                codeHistory,
                previousJudgements
        );

        AIHintResponse response = aiHintServerClient.request(sessionId, request);

        String hintContent = response.hint();
        AIHintResponse.CurrentJudgement cj = response.current_judgement();

        // judgement는 무조건 Redis 저장
        sessionCodeRedisService.appendJudgement(
                sessionId,
                PreviousJudgementRedisDto.builder()
                        .analysis(cj.analysis())
                        .mistakeType(cj.mistake_type())
                        .judgedAt(java.time.LocalDateTime.now())
                        .hint(hintContent)
                        .build()
        );

        // hint가 있을 경우만 처리
        if (hintContent == null || hintContent.isBlank()) {
            return;
        }

        Hint hint = Hint.builder()
                .session(session)
                .hintType(HintType.AUTO)
                .content(hintContent)
                .build();

        hintRepository.save(hint);

        hintService.sendAutoHint(
                sessionId,
                Map.of(
                        "hintId", hint.getId(),
                        "hintType", hint.getHintType(),
                        "content", hint.getContent(),
                        "isViewed", hint.getIsViewed(),
                        "createdAt", hint.getCreatedAt()
                )
        );
    }
}