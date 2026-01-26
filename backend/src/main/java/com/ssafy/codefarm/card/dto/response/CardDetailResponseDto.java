package com.ssafy.codefarm.card.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.card.entity.Card;

import java.time.LocalDateTime;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record CardDetailResponseDto(
        CardResponseDto card,
        MyCardStatusResponseDto myCardStatus
) {
    public static CardDetailResponseDto from(
            Card card,
            long count,
            List<LocalDateTime> history
    ) {
        return new CardDetailResponseDto(
                CardResponseDto.from(card),
                MyCardStatusResponseDto.from(count, history)
        );
    }
}
