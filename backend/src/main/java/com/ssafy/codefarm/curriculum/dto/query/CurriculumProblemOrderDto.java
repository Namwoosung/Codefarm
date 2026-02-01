package com.ssafy.codefarm.curriculum.dto.query;

public record CurriculumProblemOrderDto(
        Long problemId,
        Integer orderNo,
        String algorithm,
        Integer difficulty,
        Boolean isSolved
) {
}