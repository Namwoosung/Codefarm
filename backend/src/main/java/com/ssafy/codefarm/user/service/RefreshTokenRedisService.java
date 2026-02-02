package com.ssafy.codefarm.user.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
@RequiredArgsConstructor
public class RefreshTokenRedisService {
    private final StringRedisTemplate redisTemplate;

    private static final String PREFIX = "app:auth:refresh:";

    private String buildKey(Long userId) {
        return PREFIX + userId;
    }

    /**
     * Refresh Token 저장 (로그인 or 재발급 시)
     */
    public void save(Long userId, String refreshToken, Duration ttl) {

        String key = buildKey(userId);

        redisTemplate.opsForValue().set(key, refreshToken, ttl);
    }

    /**
     * Refresh Token 조회
     */
    public String get(Long userId) {

        return redisTemplate.opsForValue().get(buildKey(userId));
    }

    /**
     * Refresh Token 검증 (RTR 로직)
     */
    public void validate(Long userId, String refreshToken) {

        String savedToken = get(userId);

        if (savedToken == null) {
            throw new CustomException(
                    "로그인 정보가 만료되었습니다.",
                    ErrorCode.UNAUTHORIZED
            );
        }

        if (!savedToken.equals(refreshToken)) {
            // 탈취 의심 시 해당 사용자의 저장된 토큰 정보 삭제
            delete(userId);
            throw new CustomException(
                    "유효하지 않은 Refresh Token입니다.",
                    ErrorCode.INVALID_TOKEN
            );
        }
    }

    /**
     * 로그아웃 시 삭제
     */
    public void delete(Long userId) {
        redisTemplate.delete(buildKey(userId));
    }
}
