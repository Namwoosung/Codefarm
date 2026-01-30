package com.ssafy.codefarm.curriculum.dto.response;

import com.ssafy.codefarm.problem.dto.response.ProblemListItemResponseDto;

public record CurriculumRecommendResponseDto(
        Boolean isLogined,
        ProblemListItemResponseDto recommendedProblem
) {
    public static CurriculumRecommendResponseDto of(
            boolean isLogined,
            ProblemListItemResponseDto recommendedProblem
    ) {
        return new CurriculumRecommendResponseDto(isLogined, recommendedProblem);
    }
}