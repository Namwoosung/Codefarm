package com.ssafy.codefarm.hint.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.hint.entity.Hint;
import com.ssafy.codefarm.hint.entity.HintType;

import java.time.LocalDateTime;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record HintItemResponseDto(
        Long hintId,
        HintType hintType,
        String userQuestion,
        String content,
        Boolean isViewed,
        LocalDateTime createdAt
) {

    public static HintItemResponseDto from(Hint hint) {
        return new HintItemResponseDto(
                hint.getId(),
                hint.getHintType(),
                hint.getHintType() == HintType.MANUAL ? hint.getUserQuestion() : null,
                hint.getContent(),
                hint.getIsViewed(),
                hint.getCreatedAt()
        );
    }
}