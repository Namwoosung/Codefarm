package com.ssafy.codefarm.card.dto.response;


public record TopCollectorDto(
        Long userId,
        String nickname,
        Long totalCardCount
) {}