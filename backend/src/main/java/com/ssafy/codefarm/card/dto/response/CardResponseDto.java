package com.ssafy.codefarm.card.dto.response;

import com.ssafy.codefarm.card.entity.Card;
import com.ssafy.codefarm.card.entity.CardGrade;

public record CardResponseDto(
        Long cardId,
        String name,
        CardGrade grade,
        String image
) {
    public static CardResponseDto from(Card card) {
        return new CardResponseDto(
            card.getId(),
            card.getName(),
            card.getGrade(),
            card.getImage()
        );
    }
}
