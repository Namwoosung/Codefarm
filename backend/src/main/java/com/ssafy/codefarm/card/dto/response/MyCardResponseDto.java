package com.ssafy.codefarm.card.dto.response;

import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;

public record MyCardResponseDto(
        CardResponseDto card,
        Long count
) {
    public static MyCardResponseDto from(MyCardQueryDto myCardQueryDto) {
        return new MyCardResponseDto(
                new CardResponseDto(myCardQueryDto.cardId(), myCardQueryDto.no(), myCardQueryDto.name(), myCardQueryDto.grade(), myCardQueryDto.image()),
                myCardQueryDto.count()
        );
    }
}
