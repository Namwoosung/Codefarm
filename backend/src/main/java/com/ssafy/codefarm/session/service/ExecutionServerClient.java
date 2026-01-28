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

        log.info("Sending execution request to execution server: language={}, codeLength={}, stdinLength={}",
                executeServerRequest.language(),
                executeServerRequest.code().length(),
                executeServerRequest.stdin().length());

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
                .doOnSuccess(result -> {
                    log.info("Received execution result: stdoutLength={}, stderrLength={}, execTime={}ms, isTimeout={}",
                            result.stdout() != null ? result.stdout().length() : 0,
                            result.stderr() != null ? result.stderr().length() : 0,
                            result.execTime(),
                            result.isTimeout());
                    
                    if ((result.stdout() == null || result.stdout().isEmpty()) &&
                        (result.stderr() == null || result.stderr().isEmpty())) {
                        log.warn("Both stdout and stderr are empty! This might indicate an issue.");
                    }
                })
                .onErrorMap(
                        ex -> new CustomException(
                                "실행 서버 통신 실패: " + ex.getMessage(),
                                ErrorCode.EXTERNAL_API_ERROR
                        )
                );
    }
}
