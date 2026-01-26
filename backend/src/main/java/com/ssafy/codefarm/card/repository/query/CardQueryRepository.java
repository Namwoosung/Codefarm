package com.ssafy.codefarm.card.repository.query;

import com.ssafy.codefarm.card.dto.query.CardDetailQueryDto;
import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;

import java.util.List;
import java.util.Optional;

public interface CardQueryRepository {
    List<MyCardQueryDto> findMyCards(Long userId);

    Optional<CardDetailQueryDto> findCardDetail(Long userId, Long cardId);
}
