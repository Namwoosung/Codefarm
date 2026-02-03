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
import org.springframework.transaction.annotation.Transactional;

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
    private final HintProcessingService hintProcessingService;

    private final ConcurrentHashMap<Long, ScheduledFuture<?>> tasks = new ConcurrentHashMap<>();

    private static final Duration INTERVAL = Duration.ofMinutes(1); // test를 위해 1분으로 설정

    public void start(Long sessionId) {

        if (tasks.containsKey(sessionId)) {
            log.warn("Scheduler already running. sessionId={}", sessionId);
            return;
        }

        ScheduledFuture<?> future = taskScheduler.scheduleAtFixedRate(
                () -> {
                    boolean keepRunning = hintProcessingService.process(sessionId);
                    if (!keepRunning) {
                        stop(sessionId);
                    }
                },
                Instant.now().plus(INTERVAL),
                INTERVAL
        );

        tasks.put(sessionId, future);
        log.info("Auto hint scheduler started. sessionId={}", sessionId);
    }

    public void stop(Long sessionId) {
        ScheduledFuture<?> future = tasks.remove(sessionId);
        if (future != null) {
            future.cancel(true);
            log.info("Auto hint scheduler stopped. sessionId={}", sessionId);
        }
    }
}