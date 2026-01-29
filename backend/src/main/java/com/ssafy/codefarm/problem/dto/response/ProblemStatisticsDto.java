package com.ssafy.codefarm.problem.dto.response;

public record ProblemStatisticsDto(
    Long submissionCount,
    Long successCount
) {
}