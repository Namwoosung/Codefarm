package com.ssafy.codefarm.session.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.ssafy.codefarm.session.entity.Session;

import java.time.LocalDateTime;

public record SessionResponseDto(
        Long sessionId,
        String status,
        LocalDateTime startedAt,
        LocalDateTime endedAt,
        Integer maxHint,
        Integer usedHint,
        Long userId,
        Long problemId
) {

    public static SessionResponseDto from(Session session) {
        return new SessionResponseDto(
                session.getId(),
                session.getStatus().name(),
                session.getStartedAt(),
                session.getEndedAt(),
                session.getMaxHint(),
                session.getUsedHint(),
                session.getUser().getId(),
                session.getProblem().getId()
        );
    }
}