package com.ssafy.codefarm.result.repository.impl;

import com.querydsl.core.types.Projections;
import com.querydsl.jpa.impl.JPAQueryFactory;
import com.ssafy.codefarm.hint.entity.QHint;
import com.ssafy.codefarm.result.dto.query.ReportDetailQueryDto;
import com.ssafy.codefarm.result.entity.QResult;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.result.repository.ResultQueryRepository;
import com.ssafy.codefarm.session.entity.QSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import static com.ssafy.codefarm.problem.entity.QProblem.problem;

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
}
