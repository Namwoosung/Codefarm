package com.ssafy.codefarm.card.dto.query;

import com.ssafy.codefarm.card.entity.CardGrade;

public record MyCardQueryDto(
        Long cardId,
        String name,
        CardGrade grade,
        String image,
        Long count
) {
}
