package com.ssafy.codefarm.session.dto.response;

public record RunSessionResponseDto(
        String stdout,
        String stderr,
        Long memoryUsage,
        Integer execTime,
        Boolean isTimeout,
        Boolean isOom
) {
    public static RunSessionResponseDto from(
            String stdout,
            String stderr,
            Long memoryUsage,
            Integer execTime,
            Boolean isTimeout,
            Boolean isOom
    ) {
        return new RunSessionResponseDto(stdout, stderr, memoryUsage, execTime, isTimeout, isOom);
    }
}