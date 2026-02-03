package com.ssafy.codefarm.hint.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.hint.dto.ai.AIHintRequest;
import com.ssafy.codefarm.hint.dto.ai.AIHintResponse;
import com.ssafy.codefarm.hint.dto.requset.ManualHintRequestDto;
import com.ssafy.codefarm.hint.dto.response.HintItemResponseDto;
import com.ssafy.codefarm.hint.dto.response.HintListResponseDto;
import com.ssafy.codefarm.hint.dto.response.ManualHintResponseDto;
import com.ssafy.codefarm.hint.entity.Hint;
import com.ssafy.codefarm.hint.entity.HintType;
import com.ssafy.codefarm.hint.repository.HintRepository;
import com.ssafy.codefarm.hint.repository.SseEmitterRepository;
import com.ssafy.codefarm.session.dto.redis.CodeSnapshotRedisDto;
import com.ssafy.codefarm.session.dto.redis.PreviousJudgementRedisDto;
import com.ssafy.codefarm.session.entity.Session;
import com.ssafy.codefarm.session.entity.SessionStatus;
import com.ssafy.codefarm.session.repository.SessionRepository;
import com.ssafy.codefarm.session.service.SessionCodeRedisService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class HintService {

    private static final Long DEFAULT_TIMEOUT = 24 * 60L * 60 * 1000L; // 24시간

    private final SessionCodeRedisService sessionCodeRedisService;
    private final AIHintServerClient aiHintServerClient;

    private final SessionRepository sessionRepository;
    private final SseEmitterRepository emitterRepository;
    private final HintRepository hintRepository;

    @Transactional(readOnly = true)
    public SseEmitter subscribe(Long sessionId, Long userId) {

        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() ->
                        new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND)
                );

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        if (session.getStatus() != SessionStatus.ACTIVE) {
            throw new CustomException("종료된 세션에는 코드를 저장할 수 없습니다.", ErrorCode.BAD_REQUEST);
        }

        log.info("Creating new SseEmitter for sessionId={}, userId={}", sessionId, userId);
        SseEmitter emitter = new SseEmitter(DEFAULT_TIMEOUT);

        emitterRepository.save(sessionId, emitter);

        emitter.onCompletion(() -> {
            log.info("SseEmitter completed. sessionId={}", sessionId);
            emitterRepository.remove(sessionId, emitter);
        });
        emitter.onTimeout(() -> {
            log.warn("SseEmitter timed out. sessionId={}", sessionId);
            emitter.complete();
            emitterRepository.remove(sessionId, emitter);
        });
        emitter.onError(e -> {
            log.error("SseEmitter error. sessionId={}, error={}", sessionId, e.getMessage());
            emitter.completeWithError(e);
            emitterRepository.remove(sessionId, emitter);
        });

        // 503 방지용 초기 이벤트
        try {
            emitter.send(
                    SseEmitter.event()
                            .name("CONNECTED")
                            .data(Map.of(
                                    "message", "자동 힌트 구독이 시작되었습니다."
                            ))
            );
        } catch (IOException e) {
            emitterRepository.remove(sessionId, emitter);
        }

        return emitter;
    }

    public void sendAutoHint(Long sessionId, Object payload) {
        emitterRepository.send(sessionId, "AUTO_HINT", payload);
    }

    public void clearSession(Long sessionId) {
        emitterRepository.deleteAll(sessionId);
    }

    public ManualHintResponseDto createManualHint(Long sessionId, Long userId, ManualHintRequestDto requestDto) {

        Session session = sessionRepository.findByIdWithUserAndProblem(sessionId)
                .orElseThrow(() ->
                        new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND)
                );

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        if (session.getStatus() != SessionStatus.ACTIVE) {
            throw new CustomException("종료된 세션입니다.", ErrorCode.BAD_REQUEST);
        }

        // 힌트 사용 횟수 체크
        if (session.getUsedHint() >= session.getMaxHint()) {
            throw new CustomException("사용 가능한 힌트 횟수를 초과했습니다.", ErrorCode.BAD_REQUEST);
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
                requestDto.getUserQuestion(),
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

        Hint hint = Hint.builder()
                .session(session)
                .hintType(HintType.MANUAL)
                .userQuestion(requestDto.getUserQuestion())
                .content(hintContent != null ? hintContent : "")
                .isViewed(true)
                .build();

        hintRepository.save(hint);

        // 사용 횟수 증가
        session.increaseHint();

        return ManualHintResponseDto.from(
                hint,
                session.getUsedHint(),
                session.getMaxHint()
        );
    }

    @Transactional(readOnly = true)
    public HintListResponseDto getHints(Long sessionId, Long userId) {

        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() ->
                        new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND)
                );

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        List<Hint> hints =
                hintRepository.findBySessionIdOrderByCreatedAtDesc(sessionId);

        List<HintItemResponseDto> items =
                hints.stream()
                        .map(HintItemResponseDto::from)
                        .toList();

        return HintListResponseDto.from(items);
    }


    @Transactional
    public HintItemResponseDto markAsViewed(Long sessionId, Long hintId, Long userId) {

        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() ->
                        new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND)
                );

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        Hint hint = hintRepository.findById(hintId)
                .orElseThrow(() ->
                        new CustomException("힌트를 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND)
                );

        // 힌트가 해당 세션에 속해있는지 검증
        if (!hint.getSession().getId().equals(sessionId)) {
            throw new CustomException("해당 세션의 힌트가 아닙니다.", ErrorCode.FORBIDDEN);
        }

        // 이미 읽음이면 그냥 반환 (idempotent 처리)
        if (!hint.getIsViewed()) {
            hint.markAsViewed();
        }

        return HintItemResponseDto.from(hint);
    }
}