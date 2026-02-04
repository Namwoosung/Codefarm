package com.ssafy.codefarm.problem.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;
import com.ssafy.codefarm.problem.entity.ProblemType;
import java.time.LocalDateTime;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record ProblemResponseDto(
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
    LocalDateTime createdAt
) {
    public static ProblemResponseDto from(ProblemListQueryDto dto) {
        return new ProblemResponseDto(
            dto.problemId(),
            dto.title(),
            dto.description(),
            dto.concept(),
            dto.difficulty(),
            dto.algorithm(),
            dto.inputDescription(),
            dto.outputDescription(),
            dto.timeLimit(),
            dto.memoryLimit(),
            dto.exampleInput(),
            dto.exampleOutput(),
            dto.problemType(),
            dto.createdAt()
        );
    }
}