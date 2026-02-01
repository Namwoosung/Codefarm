package com.ssafy.codefarm.session.dto.execution;

public record ExecuteServerResult(
        String stdout,
        String stderr,
        Long memoryUsage,
        Integer execTime,
        Boolean isTimeout,
        Boolean isOom
) {
}