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
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Slf4j
@RequiredArgsConstructor
@Component
public class FeedbackServerClient {

    private final RestClient feedbackRestClient;

    @Value("${feedback.token}")
    private String reportServerToken;

    public String requestFeedback(
        SubmitContext context,
        SubmitSessionRequestDto requestDto
    ) {

        FeedbackRequest request = FeedbackRequest.from(context, requestDto);

        try {
            FeedbackResponse response = feedbackRestClient.post()
                    .uri("/api/v1/reports/feedback")
                    .header("X-REPORT-SERVER-TOKEN", reportServerToken)
                    .body(request)
                    .retrieve()
                    .onStatus(status -> status.isError(), (req, res) -> {
                        throw new CustomException(
                                "피드백 서버 오류",
                                ErrorCode.EXTERNAL_API_ERROR
                        );
                    })
                    .body(FeedbackResponse.class);

            String feedback = response != null ? response.feedback() : null;
            log.info("Feedback received: {}", feedback);
            return feedback;
        } catch (Exception e) {
            throw new CustomException(
                    "피드백 서버 통신 실패: " + e.getMessage(),
                    ErrorCode.EXTERNAL_API_ERROR
            );
        }
    }
}