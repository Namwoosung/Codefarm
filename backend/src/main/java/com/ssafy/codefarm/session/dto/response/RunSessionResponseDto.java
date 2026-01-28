package com.ssafy.codefarm.session.dto.response;

public record RunSessionResponseDto(
        String stdout,
        String stderr,
        Integer execTime,
        Boolean isTimeout
) {
    public static RunSessionResponseDto from(
            String stdout,
            String stderr,
            Integer execTime,
            Boolean isTimeout
    ) {
        return new RunSessionResponseDto(stdout, stderr, execTime, isTimeout);
    }
}