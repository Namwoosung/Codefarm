package com.ssafy.codefarm.session.dto.response;

import com.ssafy.codefarm.result.entity.Result;
import com.ssafy.codefarm.result.entity.ResultType;

import java.time.LocalDateTime;

public record GiveUpSessionResponseDto(
        Long resultId,
        ResultType resultType,
        String language,
        Integer solveTime,
        Integer execTime,
        Integer memory,
        String feedback,
        LocalDateTime submittedAt
) {

    public static GiveUpSessionResponseDto from(Result result) {
        return new GiveUpSessionResponseDto(
                result.getId(),
                result.getResultType(),
                result.getLanguage().name(),
                result.getSolveTime(),
                result.getExecTime(),
                result.getMemory(),
                result.getFeedback(),
                result.getCreatedAt()
        );
    }
}