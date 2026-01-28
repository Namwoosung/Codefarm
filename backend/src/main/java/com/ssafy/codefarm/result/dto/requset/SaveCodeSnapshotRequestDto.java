package com.ssafy.codefarm.result.dto.requset;

import com.ssafy.codefarm.result.entity.Language;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class SaveCodeSnapshotRequestDto {

    @NotNull(message = "language is required")
    private Language language;

    @NotBlank(message = "code is required")
    private String code;
}