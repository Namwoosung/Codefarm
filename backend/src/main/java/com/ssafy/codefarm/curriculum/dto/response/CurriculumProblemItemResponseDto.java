package com.ssafy.codefarm.curriculum.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumProblemDetailQueryDto;
import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;
import com.ssafy.codefarm.problem.dto.response.ProblemListItemResponseDto;
import com.ssafy.codefarm.problem.dto.response.ProblemResponseDto;
import com.ssafy.codefarm.problem.dto.response.ProblemStatisticsDto;
import com.ssafy.codefarm.problem.dto.response.ProblemUserStatusDto;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record CurriculumProblemItemResponseDto(
        Integer order,
        ProblemResponseDto problem,
        ProblemUserStatusDto userStatus,
        ProblemStatisticsDto statistics
) {

    public static CurriculumProblemItemResponseDto from(
            CurriculumProblemDetailQueryDto dto,
            boolean isLogined
    ) {

        ProblemListQueryDto problemListQueryDto = new ProblemListQueryDto(
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
                dto.createdAt(),
                dto.submissionCount(),
                dto.successCount(),
                dto.isSolved(),
                dto.isTried()
        );

        ProblemListItemResponseDto item =
                ProblemListItemResponseDto.from(problemListQueryDto, isLogined);

        return new CurriculumProblemItemResponseDto(
                dto.orderNo(),
                item.problem(),
                item.userStatus(),
                item.statistics()
        );
    }
}