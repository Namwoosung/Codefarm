package com.ssafy.codefarm.user.dto.response;

public record LoginResponseDto(
        UserResponseDto user,
        TokenResponseDto token
) {
    public static LoginResponseDto of(
            UserResponseDto user,
            TokenResponseDto token
    ) {
        return new LoginResponseDto(user, token);
    }
}