package com.ssafy.codefarm.problem.repository.impl;

import static com.ssafy.codefarm.problem.entity.QProblem.problem;
import static com.ssafy.codefarm.result.entity.QResult.result;
import static com.ssafy.codefarm.session.entity.QSession.session;

import com.querydsl.core.types.Projections;
import com.querydsl.core.types.dsl.BooleanExpression;
import com.querydsl.core.types.dsl.Expressions;
import com.querydsl.jpa.impl.JPAQueryFactory;
import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;
import com.ssafy.codefarm.problem.repository.ProblemQueryRepository;
import com.ssafy.codefarm.result.entity.QResult;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.session.entity.QSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class ProblemQueryRepositoryImpl implements ProblemQueryRepository {

    private final JPAQueryFactory query;

    @Override
    public ProblemListQueryDto findProblemDetail(Long problemId, Long userId) {

        QResult submitResult = new QResult("submitResult");          // SUCCESS + FAIL
        QResult successResult = new QResult("successResult");        // SUCCESS

        QSession selfSession = new QSession("selfSession");
        QResult selfSuccessResult = new QResult("selfSuccessResult");

        BooleanExpression selfUserCond = buildSelfUserCondition(userId, selfSession);

        return query
            .select(Projections.constructor(
                ProblemListQueryDto.class,
                problem.id,
                problem.title,
                problem.description,
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

                // 제출 수 = SUCCESS + FAIL
                submitResult.id.countDistinct(),

                // 성공 수 = SUCCESS
                successResult.id.countDistinct(),

                // 내 성공 여부 = SUCCESS 하나라도 존재
                userId == null
                    ? Expressions.booleanTemplate("cast(null as boolean)")
                    : selfSuccessResult.id.countDistinct().gt(0L),

                // 내 시도 여부 = 세션 존재 여부
                userId == null
                    ? Expressions.booleanTemplate("cast(null as boolean)")
                    : selfSession.id.countDistinct().gt(0L)
            ))
            .from(problem)

            // 전체 세션
            .leftJoin(session)
            .on(session.problem.id.eq(problem.id))

            // 제출 수 (SUCCESS + FAIL)
            .leftJoin(submitResult)
            .on(submitResult.session.id.eq(session.id)
                .and(submitResult.resultType.in(ResultType.SUCCESS, ResultType.FAIL)))

            // 성공 수 (SUCCESS)
            .leftJoin(successResult)
            .on(successResult.session.id.eq(session.id)
                .and(successResult.resultType.eq(ResultType.SUCCESS)))

            // 내 세션
            .leftJoin(selfSession)
            .on(selfSession.problem.id.eq(problem.id)
                .and(selfUserCond))

            // 내 성공 여부 체크용
            .leftJoin(selfSuccessResult)
            .on(selfSuccessResult.session.id.eq(selfSession.id)
                .and(selfSuccessResult.resultType.eq(ResultType.SUCCESS)))

            .where(problem.id.eq(problemId))
            .groupBy(problem.id)
            .fetchOne();
    }

    private BooleanExpression buildSelfUserCondition(Long userId, QSession selfSession) {
        if (userId == null) {
            return Expressions.FALSE.isTrue();
        }
        return selfSession.user.id.eq(userId);
    }

}
