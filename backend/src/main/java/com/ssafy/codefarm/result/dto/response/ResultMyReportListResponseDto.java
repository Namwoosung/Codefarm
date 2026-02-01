package com.ssafy.codefarm.result.dto.response;

import java.util.List;

public record ResultMyReportListResponseDto(
        PageInfo page,
        SortInfo sort,
        List<ReportDetailResponseDto> results
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