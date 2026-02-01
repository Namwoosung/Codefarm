package com.ssafy.codefarm.card.repository.query;

import com.querydsl.core.types.Projections;
import com.querydsl.jpa.impl.JPAQueryFactory;
import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;
import com.ssafy.codefarm.card.dto.response.AllCollectionMasterDto;
import com.ssafy.codefarm.card.dto.response.TodayRareCollectorDto;
import com.ssafy.codefarm.card.dto.response.TopCollectorDto;
import com.ssafy.codefarm.card.entity.CardGrade;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

import static com.ssafy.codefarm.card.entity.QCard.card;
import static com.ssafy.codefarm.card.entity.QUserCard.userCard;
import static com.ssafy.codefarm.user.entity.QUser.user;

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
                                card.no,
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

    @Override
    public List<TopCollectorDto> findTopCollectors(int limit) {

        return query
                .select(Projections.constructor(
                        TopCollectorDto.class,
                        user.id,
                        user.nickname,
                        userCard.count()
                ))
                .from(userCard)
                .join(userCard.user, user)
                .groupBy(user.id, user.nickname)
                .orderBy(userCard.count().desc())
                .limit(limit)
                .fetch();
    }

    @Override
    public List<AllCollectionMasterDto> findAllCollectionMasters() {

        long totalCardTypeCount =
                query.select(card.count())
                        .from(card)
                        .fetchOne();

        return query
                .select(Projections.constructor(
                        AllCollectionMasterDto.class,
                        user.id,
                        user.nickname,
                        userCard.card.id.countDistinct()
                                .multiply(100)
                                .divide(totalCardTypeCount)
                                .intValue()
                ))
                .from(userCard)
                .join(userCard.user, user)
                .groupBy(user.id, user.nickname)
                .having(userCard.card.id.countDistinct().eq(totalCardTypeCount))
                .fetch();
    }

    @Override
    public List<TodayRareCollectorDto> findTodayRareCollectors() {

        LocalDateTime start = LocalDate.now().atStartOfDay();
        LocalDateTime end = start.plusDays(1);

        return query
                .select(Projections.constructor(
                        TodayRareCollectorDto.class,
                        user.id,
                        user.nickname,
                        card.name,
                        card.grade
                ))
                .from(userCard)
                .join(userCard.user, user)
                .join(userCard.card, card)
                .where(
                        userCard.createdAt.between(start, end),
                        card.grade.in(CardGrade.GOLD, CardGrade.SPECIAL)
                )
                .orderBy(userCard.createdAt.desc())
                .fetch();
    }
}
