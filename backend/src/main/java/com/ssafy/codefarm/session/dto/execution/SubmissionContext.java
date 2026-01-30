package com.ssafy.codefarm.session.dto.execution;

import com.ssafy.codefarm.result.entity.Result;
import java.time.LocalDateTime;

public record SubmissionContext(
    Long resultId,
    Integer solveTime,
    Integer execTime,
    Integer memory,
    LocalDateTime submittedAt
) {

    public static SubmissionContext from(Result result) {
        return new SubmissionContext(
            result.getId(),
            result.getSolveTime(),
            result.getExecTime(),
            result.getMemory(),
            result.getCreatedAt()
        );
    }
}