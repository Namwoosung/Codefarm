package com.ssafy.codefarm.card.repository.query;

import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;
import com.ssafy.codefarm.card.dto.response.AllCollectionMasterDto;
import com.ssafy.codefarm.card.dto.response.TodayRareCollectorDto;
import com.ssafy.codefarm.card.dto.response.TopCollectorDto;

import java.time.LocalDateTime;
import java.util.List;

public interface CardQueryRepository {
    List<MyCardQueryDto> findMyCards(Long userId);

    List<LocalDateTime> findAcquiredHistory(Long userId, Long cardId);

    List<TopCollectorDto> findTopCollectors(int limit);

    List<AllCollectionMasterDto> findAllCollectionMasters();

    List<TodayRareCollectorDto> findTodayRareCollectors();
}
