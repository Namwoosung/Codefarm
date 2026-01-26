package com.ssafy.codefarm.user.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.*;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class CheckNicknameRequestDto {

    @NotBlank(message = "nickname is required")
    @Pattern(
            regexp = "^[가-힣a-zA-Z0-9_-]{2,20}$",
            message = "nickname must be 2~20 characters and contain only Korean, English, numbers, _ or -"
    )
    private String nickname;
}