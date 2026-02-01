package com.ssafy.codefarm.session.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.session.dto.execution.ExecuteServerRequest;
import com.ssafy.codefarm.session.dto.execution.ExecuteServerResult;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Slf4j
@Component
@RequiredArgsConstructor
public class ExecutionServerClient {

    private final RestClient executionRestClient;

    public ExecuteServerResult execute(ExecuteServerRequest executeServerRequest) {

        log.info("Sending execution request to execution server: language={}, codeLength={}, stdinLength={}",
                executeServerRequest.language(),
                executeServerRequest.code().length(),
                executeServerRequest.stdin().length());

        try {
            ExecuteServerResult result = executionRestClient.post()
                    .uri("/execute")
                    .body(executeServerRequest)
                    .retrieve()
                    .onStatus(status -> status.isError(), (request, response) -> {
                        throw new CustomException(
                                "실행 서버 오류",
                                ErrorCode.EXTERNAL_API_ERROR
                        );
                    })
                    .body(ExecuteServerResult.class);

            if (result != null) {
                log.info("Received execution result: stdoutLength={}, stderrLength={}, execTime={}ms, isTimeout={}",
                        result.stdout() != null ? result.stdout().length() : 0,
                        result.stderr() != null ? result.stderr().length() : 0,
                        result.execTime(),
                        result.isTimeout());

                if ((result.stdout() == null || result.stdout().isEmpty()) &&
                        (result.stderr() == null || result.stderr().isEmpty())) {
                    log.warn("Both stdout and stderr are empty! This might indicate an issue.");
                }
            }

            return result;
        } catch (CustomException e) {
            throw e;
        } catch (Exception e) {
            throw new CustomException(
                    "실행 서버 통신 실패: " + e.getMessage(),
                    ErrorCode.EXTERNAL_API_ERROR
            );
        }
    }
}
