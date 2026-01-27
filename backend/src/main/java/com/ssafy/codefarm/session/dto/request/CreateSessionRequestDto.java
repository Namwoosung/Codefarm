package com.ssafy.codefarm.session.dto.request;

import jakarta.validation.constraints.NotNull;
import lombok.*;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class CreateSessionRequestDto {

    @NotNull(message = "problemId is required")
    private Long problemId;
}