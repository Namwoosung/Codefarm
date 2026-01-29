package com.ssafy.codefarm.card.dto.response;

import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;

import java.util.List;

public record MyCardListResponseDto(
        CardSummaryResponseDto summary,
        List<MyCardResponseDto> cards
) {
    public static MyCardListResponseDto from(CardSummaryResponseDto summary, List<MyCardQueryDto> myCardQueryDtos) {
        return new MyCardListResponseDto(
                summary,
                myCardQueryDtos.stream()
                        .map(MyCardResponseDto::from)
                        .toList()
        );
    }
}
