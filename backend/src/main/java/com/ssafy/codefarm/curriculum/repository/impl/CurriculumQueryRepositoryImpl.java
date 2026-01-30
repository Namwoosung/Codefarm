package com.ssafy.codefarm.curriculum.repository.impl;

import com.querydsl.core.types.Projections;
import com.querydsl.core.types.dsl.BooleanExpression;
import com.querydsl.core.types.dsl.Expressions;
import com.querydsl.jpa.impl.JPAQueryFactory;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumDetailQueryDto;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumProblemDetailQueryDto;
import com.ssafy.codefarm.curriculum.repository.CurriculumQueryRepository;
import com.ssafy.codefarm.result.entity.QResult;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.session.entity.QSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;

import static com.ssafy.codefarm.curriculum.entity.QCurriculum.curriculum;
import static com.ssafy.codefarm.curriculum.entity.QCurriculumProblem.curriculumProblem;
import static com.ssafy.codefarm.problem.entity.QProblem.problem;
import static com.ssafy.codefarm.session.entity.QSession.session;

@Repository
@RequiredArgsConstructor
public class CurriculumQueryRepositoryImpl implements CurriculumQueryRepository {

    private final JPAQueryFactory query;

    @Override
    public CurriculumDetailQueryDto findCurriculumDetail(Long curriculumId) {

        return query
                .select(Projections.constructor(
                        CurriculumDetailQueryDto.class,
                        curriculum.id,
                        curriculum.name,
                        curriculum.description,
                        curriculum.curriculumDifficulty,
                        curriculum.createdAt,
                        curriculumProblem.id.countDistinct()
                ))
                .from(curriculum)
                .leftJoin(curriculumProblem)
                .on(curriculumProblem.curriculum.id.eq(curriculum.id))
                .where(curriculum.id.eq(curriculumId))
                .groupBy(curriculum.id)
                .fetchOne();
    }

    @Override
    public List<CurriculumProblemDetailQueryDto> findCurriculumProblemList(
            Long curriculumId,
            Long userId
    ) {

        QResult submitResult = new QResult("submitResult");
        QResult successResult = new QResult("successResult");

        QSession selfSession = new QSession("selfSession");
        QResult selfSuccessResult = new QResult("selfSuccessResult");

        BooleanExpression selfUserCond = buildSelfUserCondition(userId, selfSession);

        return query
                .select(Projections.constructor(
                        CurriculumProblemDetailQueryDto.class,
                        curriculumProblem.orderNo,

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

                        submitResult.id.countDistinct(),
                        successResult.id.countDistinct(),

                        userId == null
                                ? Expressions.booleanTemplate("cast(null as boolean)")
                                : selfSuccessResult.id.countDistinct().gt(0L),

                        userId == null
                                ? Expressions.booleanTemplate("cast(null as boolean)")
                                : selfSession.id.countDistinct().gt(0L)
                ))
                .from(curriculumProblem)
                .join(problem).on(curriculumProblem.problem.id.eq(problem.id))

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

                .where(curriculumProblem.curriculum.id.eq(curriculumId))
                .groupBy(
                        curriculumProblem.id,
                        curriculumProblem.orderNo,
                        problem.id
                )
                .orderBy(curriculumProblem.orderNo.asc())
                .fetch();
    }

    private BooleanExpression buildSelfUserCondition(Long userId, QSession selfSession) {
        if (userId == null) return Expressions.FALSE.isTrue();
        return selfSession.user.id.eq(userId);
    }
}