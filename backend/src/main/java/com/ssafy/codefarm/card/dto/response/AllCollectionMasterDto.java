package com.ssafy.codefarm.card.dto.response;

public record AllCollectionMasterDto(
        Long userId,
        String nickname,
        Integer collectionRate
) {}