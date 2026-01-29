package com.ssafy.codefarm.session.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.session.dto.execution.SubmitContext;
import com.ssafy.codefarm.session.dto.feedback.FeedbackRequest;
import com.ssafy.codefarm.session.dto.feedback.FeedbackResponse;
import com.ssafy.codefarm.session.dto.request.SubmitSessionRequestDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatusCode;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Slf4j
@RequiredArgsConstructor
@Component
public class FeedbackServerClient {

    private final WebClient feedbackWebClient;

    @Value("${feedback.token}")
    private String reportServerToken;

    public String requestFeedback(
        SubmitContext context,
        SubmitSessionRequestDto requestDto
    ) {

        FeedbackRequest request = FeedbackRequest.from(context, requestDto);

        return feedbackWebClient.post()
            .uri("/api/v1/reports/feedback")
            .header("X-REPORT-SERVER-TOKEN", reportServerToken)
            .bodyValue(request)
            .retrieve()
            .onStatus(
                HttpStatusCode::isError,
                response -> Mono.error(
                    new CustomException(
                        "피드백 서버 오류",
                        ErrorCode.EXTERNAL_API_ERROR
                    )
                )
            )
            .bodyToMono(FeedbackResponse.class)
            .map(FeedbackResponse::feedback)
            .doOnSuccess(f -> log.info("Feedback received: {}", f))
            .block(); // submit은 boundedElastic에서 실행되므로 block 허용
    }
}