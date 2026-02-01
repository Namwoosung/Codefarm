package com.ssafy.codefarm.user.dto.response;

public record TokenResponseDto(
        String accessToken,
        String tokenType
) {
    public static TokenResponseDto from(String accessToken) {
        return new TokenResponseDto(accessToken, "Bearer");
    }
}