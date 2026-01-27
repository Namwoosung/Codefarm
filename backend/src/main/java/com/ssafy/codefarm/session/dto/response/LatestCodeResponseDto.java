package com.ssafy.codefarm.session.dto.response;

import com.ssafy.codefarm.result.entity.Language;

import java.time.LocalDateTime;

public record LatestCodeResponseDto(
        String code,
        Language language,
        LocalDateTime savedAt
) {

    public static LatestCodeResponseDto from(
            String code,
            Language language,
            LocalDateTime savedAt
    ) {
        return new LatestCodeResponseDto(code, language, savedAt);
    }
}