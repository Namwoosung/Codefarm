package com.ssafy.codefarm.session.service;

import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
@RequiredArgsConstructor
public class SessionCodeRedisService {
    private final RedisTemplate<String, Object> redisTemplate;

    private static final Duration TTL = Duration.ofHours(24); // key TTL 기한

    private String buildKey(Long sessionId) {
        return "app:session:" + sessionId + ":codes";
    }

    public void initialize(Long sessionId) {
        String key = buildKey(sessionId);
        redisTemplate.delete(key);
        redisTemplate.expire(key, TTL);
    }

    public void delete(Long sessionId) {
        redisTemplate.delete(buildKey(sessionId));
    }
}
