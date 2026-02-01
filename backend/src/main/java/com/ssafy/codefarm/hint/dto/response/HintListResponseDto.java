package com.ssafy.codefarm.hint.dto.response;

import java.util.List;

public record HintListResponseDto(
        List<HintItemResponseDto> hints
) {
    public static HintListResponseDto from(List<HintItemResponseDto> items) {
        return new HintListResponseDto(items);
    }
}