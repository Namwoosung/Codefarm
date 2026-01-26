package com.ssafy.codefarm.user.dto.response;

import com.ssafy.codefarm.user.entity.User;

import java.time.LocalDateTime;

public record UserResponseDto(
        Long userId,
        String email,
        String nickname,
        Integer age,
        Integer codingLevel,
        Integer point,
        LocalDateTime createdAt
) {
    public static UserResponseDto from(User user) {
        return new UserResponseDto(
                user.getId(),
                user.getEmail(),
                user.getNickname(),
                user.getAge(),
                user.getCodingLevel(),
                user.getPoint(),
                user.getCreatedAt()
        );
    }
}
