package com.ssafy.codefarm.hint.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.hint.dto.ai.AIHintRequest;
import com.ssafy.codefarm.hint.dto.ai.AIHintResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Slf4j
@Component
@RequiredArgsConstructor
public class AIHintServerClient {

    private final RestClient aiHintRestClient;

    @Value("${ai-hint.token}")
    private String token;

    public AIHintResponse request(Long sessionId, AIHintRequest request) {

        try {
            return aiHintRestClient.post()
                    .uri("/api/v1/sessions/{sessionId}/hints/hint", sessionId)
                    .header("X-REPORT-SERVER-TOKEN", token)
                    .body(request)
                    .retrieve()
                    .onStatus(status -> status.isError(), (req, res) -> {
                        String body = new String(res.getBody().readAllBytes());
                        log.error("AI Hint Server Error: status={}, body={}", res.getStatusCode(), body);
                        throw new CustomException(
                                "AI 힌트 서버 오류: " + res.getStatusCode(),
                                ErrorCode.EXTERNAL_API_ERROR
                        );
                    })
                    .body(AIHintResponse.class);

        } catch (Exception e) {
            log.error("AI Hint Server call failed", e);
            throw new CustomException(
                    "AI 힌트 서버 통신 실패",
                    ErrorCode.EXTERNAL_API_ERROR
            );
        }
    }
}