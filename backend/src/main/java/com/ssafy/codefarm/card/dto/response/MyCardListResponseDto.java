package com.ssafy.codefarm.card.dto.response;

import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;

import java.util.List;

public record MyCardListResponseDto(
        List<MyCardResponseDto> cards
) {
    public static MyCardListResponseDto from(List<MyCardQueryDto> myCardQueryDtos) {
        return new MyCardListResponseDto(
                myCardQueryDtos.stream()
                        .map(MyCardResponseDto::from)
                        .toList()
        );
    }
}
