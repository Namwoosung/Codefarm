package com.ssafy.codefarm.curriculum.dto.query;

import java.time.LocalDateTime;

public record CurriculumDetailQueryDto(
        Long curriculumId,
        String name,
        String description,
        Integer curriculumDifficulty,
        LocalDateTime createdAt,
        Long totalProblemCount
) {
}