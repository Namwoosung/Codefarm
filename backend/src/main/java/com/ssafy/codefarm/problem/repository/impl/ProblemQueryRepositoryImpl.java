package com.ssafy.codefarm.problem.repository.impl;

import static com.ssafy.codefarm.problem.entity.QProblem.problem;
import static com.ssafy.codefarm.session.entity.QSession.session;

import com.querydsl.core.types.Order;
import com.querydsl.core.types.OrderSpecifier;
import com.querydsl.core.types.Projections;
import com.querydsl.core.types.dsl.BooleanExpression;
import com.querydsl.core.types.dsl.Expressions;
import com.querydsl.core.types.dsl.NumberExpression;
import com.querydsl.jpa.impl.JPAQueryFactory;
import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;
import com.ssafy.codefarm.problem.repository.ProblemQueryRepository;
import com.ssafy.codefarm.result.entity.QResult;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.session.entity.QSession;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class ProblemQueryRepositoryImpl implements ProblemQueryRepository {

    private final JPAQueryFactory query;

    @Override
    public Page<ProblemListQueryDto> findProblemList(
        List<Integer> difficulties,
        List<String> algorithms,
        Pageable pageable,
        Long userId
    ) {

        QResult submitResult = new QResult("submitResult");     // SUCCESS + FAIL
        QResult successResult = new QResult("successResult");   // SUCCESS

        QSession selfSession = new QSession("selfSession");
        QResult selfSuccessResult = new QResult("selfSuccessResult");

        BooleanExpression difficultyCond = buildDifficultyCondition(difficulties);
        BooleanExpression algorithmCond = buildAlgorithmCondition(algorithms);
        BooleanExpression selfUserCond = buildSelfUserCondition(userId, selfSession);

        List<ProblemListQueryDto> content = query
            .select(Projections.constructor(
                ProblemListQueryDto.class,
                problem.id,
                problem.title,
                problem.description,
                problem.concept,
                problem.difficulty,
                problem.algorithm,
                problem.inputDescription,
                problem.outputDescription,
                problem.timeLimit,
                problem.memoryLimit,
                problem.exampleInput,
                problem.exampleOutput,
                problem.problemType,
                problem.createdAt,

                // submissionCount
                submitResult.id.countDistinct(),

                // successCount
                successResult.id.countDistinct(),

                // isSolved
                userId == null
                    ? Expressions.booleanTemplate("cast(null as boolean)")
                    : selfSuccessResult.id.countDistinct().gt(0L),

                // isTried
                userId == null
                    ? Expressions.booleanTemplate("cast(null as boolean)")
                    : selfSession.id.countDistinct().gt(0L)
            ))
            .from(problem)

            // 전체 세션
            .leftJoin(session)
            .on(session.problem.id.eq(problem.id))

            // 전체 제출 (SUCCESS + FAIL)
            .leftJoin(submitResult)
            .on(submitResult.session.id.eq(session.id)
                .and(submitResult.resultType.in(ResultType.SUCCESS, ResultType.FAIL)))

            // 성공 제출
            .leftJoin(successResult)
            .on(successResult.session.id.eq(session.id)
                .and(successResult.resultType.eq(ResultType.SUCCESS)))

            // 내 세션
            .leftJoin(selfSession)
            .on(selfSession.problem.id.eq(problem.id)
                .and(selfUserCond))

            // 내 성공 여부
            .leftJoin(selfSuccessResult)
            .on(selfSuccessResult.session.id.eq(selfSession.id)
                .and(selfSuccessResult.resultType.eq(ResultType.SUCCESS)))

            .where(difficultyCond, algorithmCond)
            .groupBy(problem.id)
            .orderBy(getOrderSpecifiers(pageable, submitResult, successResult))
            .offset(pageable.getOffset())
            .limit(pageable.getPageSize())
            .fetch();

        Long total = query
            .select(problem.count())
            .from(problem)
            .where(difficultyCond, algorithmCond)
            .fetchOne();

        return new PageImpl<>(content, pageable, total == null ? 0L : total);
    }

    @Override
    public ProblemListQueryDto findProblemDetail(Long problemId, Long userId) {

        QResult submitResult = new QResult("submitResult");
        QResult successResult = new QResult("successResult");

        QSession selfSession = new QSession("selfSession");
        QResult selfSuccessResult = new QResult("selfSuccessResult");

        BooleanExpression selfUserCond = buildSelfUserCondition(userId, selfSession);

        return query
            .select(Projections.constructor(
                ProblemListQueryDto.class,
                problem.id,
                problem.title,
                problem.description,
                problem.concept,
                problem.difficulty,
                problem.algorithm,
                problem.inputDescription,
                problem.outputDescription,
                problem.timeLimit,
                problem.memoryLimit,
                problem.exampleInput,
                problem.exampleOutput,
                problem.problemType,
                problem.createdAt,

                submitResult.id.countDistinct(),
                successResult.id.countDistinct(),

                userId == null
                    ? Expressions.booleanTemplate("cast(null as boolean)")
                    : selfSuccessResult.id.countDistinct().gt(0L),

                userId == null
                    ? Expressions.booleanTemplate("cast(null as boolean)")
                    : selfSession.id.countDistinct().gt(0L)
            ))
            .from(problem)
            .leftJoin(session)
            .on(session.problem.id.eq(problem.id))
            .leftJoin(submitResult)
            .on(submitResult.session.id.eq(session.id)
                .and(submitResult.resultType.in(ResultType.SUCCESS, ResultType.FAIL)))
            .leftJoin(successResult)
            .on(successResult.session.id.eq(session.id)
                .and(successResult.resultType.eq(ResultType.SUCCESS)))
            .leftJoin(selfSession)
            .on(selfSession.problem.id.eq(problem.id)
                .and(selfUserCond))
            .leftJoin(selfSuccessResult)
            .on(selfSuccessResult.session.id.eq(selfSession.id)
                .and(selfSuccessResult.resultType.eq(ResultType.SUCCESS)))
            .where(problem.id.eq(problemId))
            .groupBy(problem.id)
            .fetchOne();
    }

    // ===============================
    // 정렬 처리 (accuracy 포함)
    // ===============================

    private OrderSpecifier<?>[] getOrderSpecifiers(
        Pageable pageable,
        QResult submitResult,
        QResult successResult
    ) {

        if (pageable.getSort().isEmpty()) {
            return new OrderSpecifier<?>[]{problem.createdAt.desc()};
        }

        return pageable.getSort().stream()
            .map(order -> {

                Order direction =
                    order.isAscending() ? Order.ASC : Order.DESC;

                switch (order.getProperty()) {

                    case "difficulty":
                        return new OrderSpecifier<>(direction, problem.difficulty);

                    case "submissionCount":
                        return new OrderSpecifier<>(
                            direction,
                            submitResult.id.countDistinct()
                        );

                    case "accuracy":
                        return buildAccuracyOrder(direction, submitResult, successResult);

                    case "createdAt":
                        return new OrderSpecifier<>(direction, problem.createdAt);

                    default:
                        return new OrderSpecifier<>(Order.DESC, problem.createdAt);
                }
            })
            .toArray(OrderSpecifier[]::new);
    }

    private OrderSpecifier<?> buildAccuracyOrder(
        Order direction,
        QResult submitResult,
        QResult successResult
    ) {

        NumberExpression<Long> submissionCount =
            submitResult.id.countDistinct();

        NumberExpression<Long> successCount =
            successResult.id.countDistinct();

        NumberExpression<Double> accuracy =
            Expressions.numberTemplate(
                Double.class,
                "case when {0} = 0 then 0 else ({1} * 1.0 / {0}) end",
                submissionCount,
                successCount
            );

        return new OrderSpecifier<>(direction, accuracy);
    }

    // 조건 빌더
    private BooleanExpression buildDifficultyCondition(List<Integer> difficulties) {
        if (difficulties == null || difficulties.isEmpty()) return null;
        return problem.difficulty.in(difficulties);
    }

    private BooleanExpression buildAlgorithmCondition(List<String> algorithms) {
        if (algorithms == null || algorithms.isEmpty()) return null;
        return problem.algorithm.in(algorithms);
    }

    private BooleanExpression buildSelfUserCondition(Long userId, QSession selfSession) {
        if (userId == null) return Expressions.FALSE.isTrue();
        return selfSession.user.id.eq(userId);
    }
}