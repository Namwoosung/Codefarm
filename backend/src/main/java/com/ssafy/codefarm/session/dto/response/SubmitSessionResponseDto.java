package com.ssafy.codefarm.session.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.result.entity.Language;
import com.ssafy.codefarm.result.entity.Result;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.session.dto.execution.SubmitOutcome;

import java.time.LocalDateTime;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record SubmitSessionResponseDto(
        Long resultId,
        ResultType resultType,
        Language language,
        Integer solveTime,
        Integer execTime,
        Integer memory,
        String feedback,
        LocalDateTime submittedAt,

        Integer passedCount,
        Integer totalCount,
        String failReason,
        String stderr,
        Boolean isTimeout,
        Boolean isOom,
        Integer failedLineNo,
        String expectedLine,
        String actualLine
) {
    public static SubmitSessionResponseDto from(Result result, SubmitOutcome outcome) {
        return new SubmitSessionResponseDto(
                result.getId(),
                result.getResultType(),
                result.getLanguage(),
                result.getSolveTime(),
                result.getExecTime(),
                result.getMemory(),
                result.getFeedback(),
                result.getCreatedAt(),
                outcome.passedCount(),
                outcome.totalCount(),
                outcome.failReason(),
                outcome.stderr(),
                outcome.isTimeout(),
                outcome.isOom(),
                outcome.failedLineNo(),
                outcome.expectedLine(),
                outcome.actualLine()
        );
    }
}