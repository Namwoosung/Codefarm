package com.ssafy.codefarm.curriculum.dto.response;

import java.util.List;

public record CurriculumListResponseDto(
        Boolean isLogined,
        List<CurriculumListItemResponseDto> curriculums
) {
}