package com.ssafy.codefarm.hint.repository;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

@Slf4j
@Component
public class SseEmitterRepository {

    private final Map<Long, List<SseEmitter>> emitters = new ConcurrentHashMap<>();

    public SseEmitter save(Long sessionId, SseEmitter emitter) {

        log.info("Saving SseEmitter for sessionId={}", sessionId);
        emitters.computeIfAbsent(sessionId, id -> new CopyOnWriteArrayList<>())
                .add(emitter);

        return emitter;
    }

    public void send(Long sessionId, String eventName, Object data) {

        List<SseEmitter> list = emitters.get(sessionId);

        if (list == null || list.isEmpty()) {
            return;
        }

        for (SseEmitter emitter : list) {
            try {
                emitter.send(
                        SseEmitter.event()
                                .name(eventName)
                                .data(data)
                );
                log.info("Sent SSE event. sessionId={}, eventName={}", sessionId, eventName);
            } catch (IOException e) {
                log.warn("SSE 전송 실패. sessionId={}", sessionId);
                remove(sessionId, emitter);
                emitter.complete();
            }
        }
    }

    public void remove(Long sessionId, SseEmitter emitter) {
        log.info("Removing SseEmitter for sessionId={}", sessionId);
        List<SseEmitter> list = emitters.get(sessionId);
        if (list != null) {
            list.remove(emitter);
            if (list.isEmpty()) {
                emitters.remove(sessionId);
                log.info("All SseEmitters removed for sessionId={}", sessionId);
            }
        }
    }

    public void deleteAll(Long sessionId) {
        emitters.remove(sessionId);
    }
}