package com.ssafy.codefarm.result.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.result.dto.query.ReportDetailQueryDto;

import java.time.LocalDateTime;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record ReportDetailResponseDto(
        Long resultId,
        String resultType,
        String language,
        ProblemSimpleDto problem,
        String code,
        Integer solveTime,
        Integer execTime,
        Integer memory,
        String feedback,
        ResultLearningDto learning,
        LocalDateTime createdAt
) {

    public static ReportDetailResponseDto from(ReportDetailQueryDto dto) {
        return new ReportDetailResponseDto(
                dto.resultId(),
                dto.resultType().name(),
                dto.language().name(),
                new ProblemSimpleDto(
                        dto.problemId(),
                        dto.title(),
                        dto.difficulty(),
                        dto.algorithm()
                ),
                dto.code(),
                dto.solveTime(),
                dto.execTime(),
                dto.memory(),
                dto.feedback(),
                new ResultLearningDto(
                        dto.usedHintCount() == null ? 0 : dto.usedHintCount().intValue(),
                        dto.failCount() == null ? 0 : dto.failCount().intValue()
                ),
                dto.createdAt()
        );
    }
}