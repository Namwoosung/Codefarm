package com.ssafy.codefarm.session.dto.response;

import java.util.List;

public record SessionResultsResponseDto(
        List<SessionResultItemResponseDto> results
) {

    public static SessionResultsResponseDto from(
            List<SessionResultItemResponseDto> results
    ) {
        return new SessionResultsResponseDto(results);
    }
}