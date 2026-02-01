package com.ssafy.codefarm.session.dto.request;

import com.ssafy.codefarm.result.entity.Language;
import jakarta.validation.constraints.NotNull;
import lombok.*;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class GiveUpSessionRequestDto {

    @NotNull
    private Language language;

    private String code;
}