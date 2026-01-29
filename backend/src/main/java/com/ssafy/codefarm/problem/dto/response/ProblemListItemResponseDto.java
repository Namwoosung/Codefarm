package com.ssafy.codefarm.problem.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record ProblemListItemResponseDto(
    ProblemResponseDto problem,
    ProblemUserStatusDto userStatus,
    ProblemStatisticsDto statistics
) {
    public static ProblemListItemResponseDto from(
        ProblemListQueryDto dto,
        boolean isLogined
    ) {

        ProblemUserStatusDto status = null;

        if (isLogined) {
            status = new ProblemUserStatusDto(
                dto.isSolved(),
                dto.isTried()
            );
        }

        return new ProblemListItemResponseDto(
            ProblemResponseDto.from(dto),
            status,
            new ProblemStatisticsDto(
                dto.submissionCount(),
                dto.successCount()
            )
        );
    }
}