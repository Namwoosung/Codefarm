package com.ssafy.codefarm.hint.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.hint.repository.SseEmitterRepository;
import com.ssafy.codefarm.session.entity.Session;
import com.ssafy.codefarm.session.entity.SessionStatus;
import com.ssafy.codefarm.session.repository.SessionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.Map;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class HintService {

    private static final Long DEFAULT_TIMEOUT = 6 * 60L * 60 * 1000L; // 6시간

    private final SessionRepository sessionRepository;
    private final SseEmitterRepository emitterRepository;

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

        SseEmitter emitter = new SseEmitter(DEFAULT_TIMEOUT);

        emitterRepository.save(sessionId, emitter);

        emitter.onCompletion(() -> emitterRepository.remove(sessionId, emitter));
        emitter.onTimeout(() -> {
            emitter.complete();
            emitterRepository.remove(sessionId, emitter);
        });
        emitter.onError(e -> {
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
}