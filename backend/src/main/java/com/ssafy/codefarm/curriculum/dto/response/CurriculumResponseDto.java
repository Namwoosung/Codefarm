package com.ssafy.codefarm.curriculum.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumDetailQueryDto;

import java.time.LocalDateTime;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record CurriculumResponseDto(
        Long curriculumId,
        String name,
        String description,
        Integer curriculumDifficulty,
        Integer totalProblemCount,
        Integer solvedProblemCount,
        LocalDateTime createdAt,
        List<CurriculumProblemItemResponseDto> problems
) {

    public static CurriculumResponseDto from(
            CurriculumDetailQueryDto dto,
            Integer solvedProblemCount,
            List<CurriculumProblemItemResponseDto> problems
    ) {
        return new CurriculumResponseDto(
                dto.curriculumId(),
                dto.name(),
                dto.description(),
                dto.curriculumDifficulty(),
                dto.totalProblemCount() == null ? 0 : dto.totalProblemCount().intValue(),
                solvedProblemCount,
                dto.createdAt(),
                problems
        );
    }
}