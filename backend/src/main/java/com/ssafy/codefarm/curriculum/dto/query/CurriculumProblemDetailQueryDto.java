package com.ssafy.codefarm.curriculum.dto.query;

import com.ssafy.codefarm.problem.entity.ProblemType;

import java.time.LocalDateTime;

public record CurriculumProblemDetailQueryDto(
        Integer orderNo,

        Long problemId,
        String title,
        String description,
        String concept,
        Integer difficulty,
        String algorithm,
        String inputDescription,
        String outputDescription,
        Integer timeLimit,
        Integer memoryLimit,
        String exampleInput,
        String exampleOutput,
        ProblemType problemType,
        LocalDateTime createdAt,

        Long submissionCount,
        Long successCount,
        Boolean isSolved,
        Boolean isTried
) {
}
