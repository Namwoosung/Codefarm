package com.ssafy.codefarm.card.dto.response;

import java.util.Map;

public record CardSummaryResponseDto(
        long totalMyCard,
        long totalServiceCard,
        Map<String, Long> gradeCounts
) {
}
