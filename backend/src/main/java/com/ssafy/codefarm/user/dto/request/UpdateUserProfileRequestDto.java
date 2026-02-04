package com.ssafy.codefarm.user.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;
import lombok.*;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class UpdateUserProfileRequestDto {

    @Pattern(
            regexp = "^[가-힣a-zA-Z0-9_-]{2,20}$",
            message = "INVALID_PARAMETER"
    )
    private String nickname;

    @Pattern(regexp = "^[가-힣a-zA-Z]{2,20}$", message = "INVALID_PARAMETER")
    private String name;

    @Min(value = 0, message = "INVALID_PARAMETER")
    @Max(value = 150, message = "INVALID_PARAMETER")
    private Integer age;

    @Min(value = 1, message = "codingLevel must be between 1 and 5")
    @Max(value = 5, message = "codingLevel must be between 1 and 5")
    private Integer codingLevel;
}