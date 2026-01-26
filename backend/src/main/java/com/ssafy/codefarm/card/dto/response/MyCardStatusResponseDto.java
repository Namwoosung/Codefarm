package com.ssafy.codefarm.card.dto.response;

import java.time.LocalDateTime;
import java.util.List;

public record MyCardStatusResponseDto(
        long count,
        List<AcquiredHistoryDto> acquiredHistory
) {
    public static MyCardStatusResponseDto from(
            long count,
            List<LocalDateTime> history
    ) {
        return new MyCardStatusResponseDto(
                count,
                history.stream()
                        .map(AcquiredHistoryDto::new)
                        .toList()
        );
    }

    public record AcquiredHistoryDto(
            LocalDateTime acquiredAt
    ) {}
}
