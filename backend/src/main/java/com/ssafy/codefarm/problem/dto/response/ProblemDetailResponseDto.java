package com.ssafy.codefarm.problem.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record ProblemDetailResponseDto(
    Boolean isLogined,
    ProblemResponseDto problem,
    ProblemUserStatusDto userStatus,
    ProblemStatisticsDto statistics
) {

    public static ProblemDetailResponseDto from(
        ProblemListItemResponseDto item,
        boolean isLogined
    ) {
        return new ProblemDetailResponseDto(
            isLogined,
            item.problem(),
            item.userStatus(),
            item.statistics()
        );
    }
}