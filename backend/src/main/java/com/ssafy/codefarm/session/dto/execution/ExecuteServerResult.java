package com.ssafy.codefarm.session.dto.execution;

public record ExecuteServerResult(
        String stdout,
        String stderr,
        Integer execTime,
        Boolean isTimeout
) {
}