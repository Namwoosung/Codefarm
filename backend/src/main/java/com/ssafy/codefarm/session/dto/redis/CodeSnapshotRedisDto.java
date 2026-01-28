package com.ssafy.codefarm.session.dto.redis;

import com.ssafy.codefarm.result.entity.Language;
import lombok.*;

import java.io.Serializable;
import java.time.LocalDateTime;

@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class CodeSnapshotRedisDto implements Serializable {

    private Language language;
    private String code;
    private LocalDateTime savedAt;
}