package com.ssafy.codefarm.card.dto.response;

import java.util.List;

public record CardRankingResponseDto(
        List<TopCollectorDto> topCollectors,
        List<AllCollectionMasterDto> allCollectionMasters,
        List<TodayRareCollectorDto> todayRareCollectors
) {}