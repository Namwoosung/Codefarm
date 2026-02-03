package com.ssafy.codefarm.session.dto.redis;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class PreviousJudgementRedisDto {
    private String analysis;
    private LocalDateTime judgedAt;
    private List<String> mistakeType;
    private String hint;
}
