package com.ssafy.codefarm.card.entity;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

import java.util.Arrays;
import java.util.concurrent.ThreadLocalRandom;

@Getter
@RequiredArgsConstructor
public enum CardGrade {

    BRONZE(70),
    SILVER(25),
    GOLD(5);

    private final int weight;

    private static final int TOTAL_WEIGHT =
            Arrays.stream(values()).mapToInt(CardGrade::getWeight).sum();

    public static CardGrade pickRandom() {
        int random = ThreadLocalRandom.current().nextInt(TOTAL_WEIGHT);
        int cumulative = 0;

        for (CardGrade grade : values()) {
            cumulative += grade.weight;
            if (random < cumulative) {
                return grade;
            }
        }

        throw new CustomException("CardGrade 랜덤 선택 실패", ErrorCode.INTERNAL_SERVER_ERROR);
    }
}