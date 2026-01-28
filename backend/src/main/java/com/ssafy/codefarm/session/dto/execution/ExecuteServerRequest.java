package com.ssafy.codefarm.session.dto.execution;

import com.ssafy.codefarm.result.entity.Language;

public record ExecuteServerRequest(
        Language language,
        String code,
        String stdin,
        Integer timeLimitMs,
        Integer memoryLimitMb,
        Double cpuLimit
) {
}