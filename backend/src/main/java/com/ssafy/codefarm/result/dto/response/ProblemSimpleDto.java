package com.ssafy.codefarm.result.dto.response;

public record ProblemSimpleDto(
        Long problemId,
        String title,
        Integer difficulty,
        String algorithm
) {
}