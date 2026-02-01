package com.ssafy.codefarm.session.dto.response;

import com.ssafy.codefarm.result.entity.Result;

import java.time.LocalDateTime;

public record SessionResultItemResponseDto(
        Long resultId,
        String resultType,
        String language,
        Integer solveTime,
        Integer execTime,
        Integer memory,
        String feedback,
        LocalDateTime submittedAt
) {

    public static SessionResultItemResponseDto from(Result result) {
        return new SessionResultItemResponseDto(
                result.getId(),
                result.getResultType().name(),
                result.getLanguage().name(),
                result.getSolveTime(),
                result.getExecTime(),
                result.getMemory(),
                result.getFeedback(),
                result.getCreatedAt()
        );
    }
}