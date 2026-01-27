package com.ssafy.codefarm.result.dto.response;

import java.time.LocalDateTime;

public record SaveCodeSnapshotResponseDto(
        LocalDateTime savedAt
) {

    public static SaveCodeSnapshotResponseDto from(LocalDateTime savedAt) {
        return new SaveCodeSnapshotResponseDto(savedAt);
    }
}