package com.ssafy.codefarm.session.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.session.dto.execution.ExecuteServerRequest;
import com.ssafy.codefarm.session.dto.execution.ExecuteServerResult;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatusCode;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Slf4j
@Component
@RequiredArgsConstructor
public class ExecutionServerClient {

    private final WebClient executionWebClient;

    public Mono<ExecuteServerResult> execute(ExecuteServerRequest executeServerRequest) {

        return executionWebClient.post()
                .uri("/execute")
                .bodyValue(executeServerRequest)
                .retrieve()
                .onStatus(
                        HttpStatusCode::isError,
                        response -> Mono.error(
                                new CustomException(
                                        "실행 서버 오류",
                                        ErrorCode.EXTERNAL_API_ERROR
                                )
                        )
                )
                .bodyToMono(ExecuteServerResult.class)
                .onErrorMap(
                        ex -> new CustomException(
                                "실행 서버 통신 실패",
                                ErrorCode.EXTERNAL_API_ERROR
                        )
                );
    }
}
