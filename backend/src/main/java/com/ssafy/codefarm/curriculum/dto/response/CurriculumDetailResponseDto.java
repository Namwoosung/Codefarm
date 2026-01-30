package com.ssafy.codefarm.curriculum.dto.response;

import java.util.List;

public record CurriculumDetailResponseDto(
        Boolean isLogined,
        List<CurriculumResponseDto> curriculums
) {
    public static CurriculumDetailResponseDto from(
            boolean isLogined,
            CurriculumResponseDto curriculum
    ) {
        return new CurriculumDetailResponseDto(isLogined, List.of(curriculum));
    }
}