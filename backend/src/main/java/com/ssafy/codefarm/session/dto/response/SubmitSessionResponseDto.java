package com.ssafy.codefarm.session.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.session.dto.execution.EvaluationContext;
import com.ssafy.codefarm.session.dto.execution.SubmissionContext;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record SubmitSessionResponseDto(
    ResultType resultType,
    EvaluationContext evaluationContext,
    SubmissionContext submissionContext,
    String feedback,
    Integer awardedPoints
) {

    public static SubmitSessionResponseDto success(
        SubmissionContext submissionContext,
        EvaluationContext evaluationContext,
        String feedback,
        Integer awardedPoints
    ) {
        return new SubmitSessionResponseDto(
            ResultType.SUCCESS,
            evaluationContext,
            submissionContext,
            feedback,
            awardedPoints
        );
    }

    public static SubmitSessionResponseDto fail(
        EvaluationContext evaluationContext
    ) {
        return new SubmitSessionResponseDto(
            ResultType.FAIL,
            evaluationContext,
            null,
            null,
            null
        );
    }
}