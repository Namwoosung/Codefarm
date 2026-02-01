package com.ssafy.codefarm.card.dto.response;

import com.ssafy.codefarm.card.entity.CardGrade;

public record TodayRareCollectorDto(
        Long userId,
        String nickname,
        String cardName,
        CardGrade grade
) {}