package com.ssafy.codefarm.curriculum.dto.response;

import java.util.List;

public record CurriculumDetailResponseDto(
        Boolean isLogined,
        CurriculumResponseDto curriculum
) {
    public static CurriculumDetailResponseDto from(
            boolean isLogined,
            CurriculumResponseDto curriculum
    ) {
        return new CurriculumDetailResponseDto(isLogined, curriculum);
    }
}