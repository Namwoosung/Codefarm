package com.ssafy.codefarm.card.repository.query;

import com.querydsl.jpa.impl.JPAQueryFactory;
import com.ssafy.codefarm.card.dto.query.CardDetailQueryDto;
import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;
import com.ssafy.codefarm.card.entity.QCard;
import com.ssafy.codefarm.card.entity.QUserCard;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

import static com.ssafy.codefarm.card.entity.QCard.*;
import static com.ssafy.codefarm.card.entity.QUserCard.*;

@Repository
@RequiredArgsConstructor
public class CardQueryRepositoryImpl implements CardQueryRepository{

    private final JPAQueryFactory query;

    @Override
    public List<MyCardQueryDto> findMyCards(Long userId) {
        return null;
    }

    @Override
    public Optional<CardDetailQueryDto> findCardDetail(Long userId, Long cardId) {
        return Optional.empty();
    }
}
