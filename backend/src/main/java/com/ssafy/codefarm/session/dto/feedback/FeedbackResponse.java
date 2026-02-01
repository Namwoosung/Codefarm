package com.ssafy.codefarm.session.dto.feedback;

public record FeedbackResponse(
    String request_id,
    String feedback
) {}