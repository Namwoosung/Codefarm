package com.ssafy.codefarm.user.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.user.entity.User;

import java.time.LocalDateTime;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record UserSignupResponseDto(
        Long userId,
        String email,
        String nickname,
        Integer age,
        Integer codingLevel,
        Integer point,
        LocalDateTime createdAt
) {

    public static UserSignupResponseDto from(User user) {
        return new UserSignupResponseDto(
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