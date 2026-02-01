package com.ssafy.codefarm.curriculum.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.problem.dto.response.ProblemListItemResponseDto;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record CurriculumListItemResponseDto(
        CurriculumResponseDto curriculum,
        ProblemListItemResponseDto recommendedProblem
) {
}