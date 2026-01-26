package com.ssafy.codefarm.card.dto.query;

import com.ssafy.codefarm.card.entity.CardGrade;

import java.time.LocalDateTime;
import java.util.List;

public record CardDetailQueryDto(
        Long cardId,
        String name,
        CardGrade grade,
        String image,
        Long count,
        List<AcquiredHistoryDto> acquiredHistory
) {
    public record AcquiredHistoryDto(
            LocalDateTime acquiredAt
    ) {}
}
