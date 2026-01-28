package com.ssafy.codefarm.session.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.session.dto.redis.CodeSnapshotRedisDto;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
@RequiredArgsConstructor
public class SessionCodeRedisService {

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    private static final Duration TTL = Duration.ofHours(24); // key TTL 기한

    private String buildKey(Long sessionId) {
        return "app:session:" + sessionId + ":codes";
    }

    public void initialize(Long sessionId) {
        redisTemplate.delete(buildKey(sessionId));
    }

    public void appendSnapshot(Long sessionId, CodeSnapshotRedisDto snapshot) {

        String key = buildKey(sessionId);

        try {
            String json = objectMapper.writeValueAsString(snapshot);

            redisTemplate.opsForList().rightPush(key, json);

            redisTemplate.expire(key, TTL);

        } catch (JsonProcessingException e) {
            throw new CustomException(
                    "코드 스냅샷 직렬화 실패",
                    ErrorCode.INTERNAL_SERVER_ERROR
            );
        }
    }

    public CodeSnapshotRedisDto getLatestSnapshot(Long sessionId) {

        String key = buildKey(sessionId);

        String json = redisTemplate.opsForList().index(key, -1);

        if (json == null) {
            return null;
        }

        try {
            return objectMapper.readValue(json, CodeSnapshotRedisDto.class);
        } catch (JsonProcessingException e) {
            throw new CustomException(
                    "코드 스냅샷 역직렬화 실패",
                    ErrorCode.INTERNAL_SERVER_ERROR
            );
        }
    }

    public void delete(Long sessionId) {
        redisTemplate.delete(buildKey(sessionId));
    }
}
