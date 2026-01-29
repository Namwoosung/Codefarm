package com.ssafy.codefarm.problem.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record ProblemListResponseDto(
    Boolean isLogined,
    PageInfo page,
    SortInfo sort,
    List<ProblemListItemResponseDto> problemList
) {

    public record PageInfo(
        int number,
        int size,
        long totalElements,
        int totalPages
    ) {}

    public record SortInfo(
        String by,
        String direction
    ) {}
}