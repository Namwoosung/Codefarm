package com.ssafy.codefarm.hint.dto.requset;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class ManualHintRequestDto {

    @NotBlank(message = "userQuestion is required")
    private String userQuestion;
}