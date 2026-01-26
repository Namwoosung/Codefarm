package com.ssafy.codefarm.card.dto.response;

import com.ssafy.codefarm.card.entity.Card;

public record DrawCardResponseDto(
        CardResponseDto card,
        boolean isNew
) {
    public static DrawCardResponseDto from(Card card, boolean isNew){
        return new DrawCardResponseDto(
                CardResponseDto.from(card),
                isNew
        );
    }
}
