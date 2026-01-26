package com.ssafy.codefarm.card.repository.query;

import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;

import java.time.LocalDateTime;
import java.util.List;

public interface CardQueryRepository {
    List<MyCardQueryDto> findMyCards(Long userId);

    List<LocalDateTime> findAcquiredHistory(Long userId, Long cardId);
}
