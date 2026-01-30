package com.ssafy.codefarm.session.dto.execution;

public record EvaluationContext(
    Integer passedCount,
    Integer totalCount,
    String failReason,
    Boolean isTimeout,
    Boolean isOom,
    Integer failedLineNo,
    String expectedLine,
    String actualLine
) {

    public static EvaluationContext from(SubmitOutcome outcome) {
        return new EvaluationContext(
            outcome.passedCount(),
            outcome.totalCount(),
            outcome.failReason(),
            outcome.isTimeout(),
            outcome.isOom(),
            outcome.failedLineNo(),
            outcome.expectedLine(),
            outcome.actualLine()
        );
    }
}