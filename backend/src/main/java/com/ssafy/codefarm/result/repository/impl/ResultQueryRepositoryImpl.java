package com.ssafy.codefarm.result.repository.impl;

import com.querydsl.core.types.Order;
import com.querydsl.core.types.OrderSpecifier;
import com.querydsl.core.types.Projections;
import com.querydsl.core.types.dsl.BooleanExpression;
import com.querydsl.jpa.impl.JPAQueryFactory;
import com.ssafy.codefarm.hint.entity.HintType;
import com.ssafy.codefarm.hint.entity.QHint;
import com.ssafy.codefarm.result.dto.query.ReportDetailQueryDto;
import com.ssafy.codefarm.result.entity.QResult;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.result.repository.ResultQueryRepository;
import com.ssafy.codefarm.session.entity.QSession;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

import java.util.List;

import static com.ssafy.codefarm.hint.entity.QHint.hint;
import static com.ssafy.codefarm.problem.entity.QProblem.problem;
import static com.ssafy.codefarm.result.entity.QResult.result;
import static com.ssafy.codefarm.session.entity.QSession.session;

@Repository
@RequiredArgsConstructor
public class ResultQueryRepositoryImpl implements ResultQueryRepository {

    private final JPAQueryFactory query;

    @Override
    public ReportDetailQueryDto findReportDetail(Long resultId, Long userId) {

        QResult result = QResult.result;
        QResult failResult = new QResult("failResult");
        QSession session = QSession.session;
        QHint hint = QHint.hint;

        return query
                .select(Projections.constructor(
                        ReportDetailQueryDto.class,
                        result.id,
                        result.resultType,
                        result.language,

                        problem.id,
                        problem.title,
                        problem.difficulty,
                        problem.algorithm,

                        result.code,
                        result.solveTime,
                        result.execTime,
                        result.memory,
                        result.feedback,

                        hint.id.countDistinct(),
                        failResult.id.countDistinct(),

                        result.createdAt
                ))
                .from(result)
                .join(result.session, session)
                .join(session.problem, problem)

                .leftJoin(hint)
                .on(hint.session.id.eq(session.id)
                        .and(hint.isViewed.isTrue()))

                .leftJoin(failResult)
                .on(failResult.session.id.eq(session.id)
                        .and(failResult.resultType.eq(ResultType.FAIL)))

                .where(
                        result.id.eq(resultId),
                        session.user.id.eq(userId)
                )
                .groupBy(
                        result.id,
                        problem.id,
                        session.id
                )
                .fetchOne();
    }

    @Override
    public Page<ReportDetailQueryDto> findMyReportList(
            Long userId,
            ResultType resultType,
            Pageable pageable
    ) {

        QResult failResult = new QResult("failResult");

        BooleanExpression ownerCond = session.user.id.eq(userId);
        BooleanExpression reportTypeBaseCond = result.resultType.in(ResultType.SUCCESS, ResultType.GIVE_UP);
        BooleanExpression reportTypeCond = buildResultTypeCondition(resultType);

        List<ReportDetailQueryDto> content = query
                .select(Projections.constructor(
                        ReportDetailQueryDto.class,
                        result.id,
                        result.resultType,
                        result.language,

                        problem.id,
                        problem.title,
                        problem.difficulty,
                        problem.algorithm,

                        result.code,
                        result.solveTime,
                        result.execTime,
                        result.memory,
                        result.feedback,

                        hint.id.countDistinct(),

                        failResult.id.countDistinct(),

                        result.createdAt
                ))
                .from(result)
                .join(result.session, session)
                .join(session.problem, problem)

                .leftJoin(hint)
                .on(hint.session.id.eq(session.id)
                        .and(hint.isViewed.isTrue())
                        .and(hint.hintType.in(HintType.MANUAL, HintType.AUTO)))

                .leftJoin(failResult)
                .on(failResult.session.id.eq(session.id)
                        .and(failResult.resultType.eq(ResultType.FAIL)))

                .where(ownerCond, reportTypeBaseCond, reportTypeCond)
                .groupBy(result.id, problem.id)
                .orderBy(getOrderSpecifiers(pageable))
                .offset(pageable.getOffset())
                .limit(pageable.getPageSize())
                .fetch();

        Long total = query
                .select(result.id.count())
                .from(result)
                .join(result.session, session)
                .where(ownerCond, reportTypeBaseCond, reportTypeCond)
                .fetchOne();

        return new PageImpl<>(content, pageable, total == null ? 0L : total);
    }

    private BooleanExpression buildResultTypeCondition(ResultType resultType) {
        if (resultType == null) {
            return null;
        }

        return result.resultType.eq(resultType);
    }

    private OrderSpecifier<?>[] getOrderSpecifiers(Pageable pageable) {
        if (pageable.getSort().isEmpty()) {
            return new OrderSpecifier<?>[]{result.createdAt.desc()};
        }

        return pageable.getSort().stream()
                .map(order -> {

                    Order direction = order.isAscending() ? Order.ASC : Order.DESC;

                    return switch (order.getProperty()) {
                        case "createdAt" -> new OrderSpecifier<>(direction, result.createdAt);
                        default -> new OrderSpecifier<>(Order.DESC, result.createdAt);
                    };
                })
                .toArray(OrderSpecifier[]::new);
    }
}
