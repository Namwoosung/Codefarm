package com.ssafy.codefarm.curriculum.repository;

import com.ssafy.codefarm.curriculum.dto.query.CurriculumDetailQueryDto;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumProblemDetailQueryDto;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumProblemOrderDto;
import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;

import java.util.List;

public interface CurriculumQueryRepository {
    CurriculumDetailQueryDto findCurriculumDetail(Long curriculumId);

    List<CurriculumProblemDetailQueryDto> findCurriculumProblemList(Long curriculumId, Long userId);

    List<CurriculumProblemOrderDto> findCurriculumProblemOrders(Long curriculumId, Long userId);

    ProblemListQueryDto findRandomRecommendedProblem(String algorithm, Integer blockedDifficulty, Long userId);
}
