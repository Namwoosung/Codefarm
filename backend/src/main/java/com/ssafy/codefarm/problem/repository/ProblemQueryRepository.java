package com.ssafy.codefarm.problem.repository;

import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;

public interface ProblemQueryRepository {

    ProblemListQueryDto findProblemDetail(Long problemId, Long userId);
}
