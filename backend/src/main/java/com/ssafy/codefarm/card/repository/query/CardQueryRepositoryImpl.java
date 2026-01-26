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
        return query
                .select(
                        com.querydsl.core.types.Projections.constructor(
                                MyCardQueryDto.class,
                                card.id,
                                card.name,
                                card.grade,
                                card.image,
                                userCard.id.count()
                        )
                )
                .from(userCard)
                .join(userCard.card, card)
                .where(userCard.user.id.eq(userId))
                .groupBy(card.id)
                .fetch();
    }

    @Override
    public Optional<CardDetailQueryDto> findCardDetail(Long userId, Long cardId) {
        return Optional.empty();
    }
}
