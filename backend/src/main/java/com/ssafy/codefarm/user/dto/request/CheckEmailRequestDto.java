package com.ssafy.codefarm.user.dto.request;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class CheckEmailRequestDto {

    @NotBlank(message = "email is required")
    @Email(message = "invalid email format")
    private String email;
}