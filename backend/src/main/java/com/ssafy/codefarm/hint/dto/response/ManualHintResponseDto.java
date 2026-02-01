package com.ssafy.codefarm.hint.dto.response;

import com.ssafy.codefarm.hint.entity.Hint;
import com.ssafy.codefarm.hint.entity.HintType;

import java.time.LocalDateTime;

public record ManualHintResponseDto(
        Long hintId,
        HintType hintType,
        String userQuestion,
        String content,
        Integer usedHint,
        Integer maxHint,
        Boolean isViewed,
        LocalDateTime createdAt
) {
    public static ManualHintResponseDto from(
            Hint hint,
            Integer usedHint,
            Integer maxHint
    ) {
        return new ManualHintResponseDto(
                hint.getId(),
                hint.getHintType(),
                hint.getUserQuestion(),
                hint.getContent(),
                usedHint,
                maxHint,
                hint.getIsViewed(),
                hint.getCreatedAt()
        );
    }
}
