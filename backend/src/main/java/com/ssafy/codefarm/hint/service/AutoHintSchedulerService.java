package com.ssafy.codefarm.hint.service;

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

        if (session == null || session.getStatus() != SessionStatus.ACTIVE) {
            stop(sessionId);
            return;
        }

        // Redis 데이터 조회
        List<CodeSnapshotRedisDto> codeHistory =
                sessionCodeRedisService.getSnapshots(sessionId);

        List<PreviousJudgementRedisDto> previousJudgements =
                sessionCodeRedisService.getPreviousJudgements(sessionId);

        // AI 요청 DTO 구성 (추후 실제 구현)
        /*
        AIHintRequest request = AIHintRequest.builder()
                .startedAt(session.getStartedAt())
                .observedAt(LocalDateTime.now())
                .language(extractLanguage(codeHistory))
                .userInformation(...)
                .problemInformation(...)
                .codeHistory(codeHistory)
                .previousJudgement(previousJudgements)
                .build();
        */

        // ====================================
        // AI 호출 부분 (현재는 주석)
        // AIHintResponse response = feedbackServerClient.requestAutoHint(request);
        // ====================================


        // 🔹 테스트용 더미 응답
        String analysis = "아직 코드 작성이 충분하지 않습니다.";
        List<String> mistakeTypes = List.of("NoCode_Early");
        String hintContent = "입력 처리 순서를 다시 확인해보세요.";

        // judgement는 무조건 Redis 저장
        sessionCodeRedisService.appendJudgement(
                sessionId,
                PreviousJudgementRedisDto.builder()
                        .analysis(analysis)
                        .mistakeType(mistakeTypes)
                        .judgedAt(LocalDateTime.now())
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