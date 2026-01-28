package com.ssafy.codefarm.session.dto.request;

import com.ssafy.codefarm.result.entity.Language;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class SubmitSessionRequestDto {

    @NotNull(message = "language is required")
    private Language language;

    @NotBlank(message = "code is required")
    private String code;
}