package com.ssafy.codefarm.user.dto.request;

import jakarta.validation.constraints.*;
import lombok.*;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class UserSignupRequestDto {

    @NotBlank(message = "email is required")
    @Email(message = "invalid email format")
    private String email;

    @NotBlank(message = "password is required")
    @Pattern(
            regexp = "^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,16}$",
            message = "password must contain letters, numbers, special characters (8~16)"
    )
    private String password;

    @NotBlank(message = "name is required")
    @Pattern(regexp = "^[가-힣a-zA-Z]{2,20}$", message = "name must be 2~20 characters (Korean, English)")
    private String name;

    @NotBlank(message = "nickname is required")
    @Pattern(
            regexp = "^[a-zA-Z0-9가-힣_-]{2,20}$",
            message = "nickname must be 2~20 characters (Korean, English, number, _, -)"
    )
    private String nickname;

    @NotNull(message = "age is required")
    @Min(value = 0, message = "age must be greater than or equal to 0")
    @Max(value = 150, message = "age must be less than or equal to 150")
    private Integer age;

    @NotNull(message = "codingLevel is required")
    @Min(value = 1, message = "codingLevel must be between 1 and 5")
    @Max(value = 5, message = "codingLevel must be between 1 and 5")
    private Integer codingLevel;
}