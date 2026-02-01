package com.ssafy.codefarm.result.dto.query;

import com.ssafy.codefarm.result.entity.Language;
import com.ssafy.codefarm.result.entity.ResultType;

import java.time.LocalDateTime;

public record ReportDetailQueryDto(
        Long resultId,
        ResultType resultType,
        Language language,

        Long problemId,
        String title,
        Integer difficulty,
        String algorithm,

        String code,
        Integer solveTime,
        Integer execTime,
        Integer memory,
        String feedback,

        Long usedHintCount,
        Long failCount,

        LocalDateTime createdAt
) {
}