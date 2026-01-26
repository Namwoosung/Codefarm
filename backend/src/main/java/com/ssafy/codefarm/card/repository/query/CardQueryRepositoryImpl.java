package com.ssafy.codefarm.card.repository.query;

import com.querydsl.jpa.impl.JPAQueryFactory;
import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

import static com.ssafy.codefarm.card.entity.QCard.card;
import static com.ssafy.codefarm.card.entity.QUserCard.userCard;

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
    public List<LocalDateTime> findAcquiredHistory(Long userId, Long cardId) {

        return query
                .select(userCard.createdAt)
                .from(userCard)
                .where(
                        userCard.user.id.eq(userId),
                        userCard.card.id.eq(cardId)
                )
                .orderBy(userCard.createdAt.desc())
                .fetch();
    }
}
