package com.ssafy.codefarm.curriculum.repository;

import com.ssafy.codefarm.curriculum.dto.query.CurriculumDetailQueryDto;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumProblemDetailQueryDto;

import java.util.List;

public interface CurriculumQueryRepository {
    CurriculumDetailQueryDto findCurriculumDetail(Long curriculumId);

    List<CurriculumProblemDetailQueryDto> findCurriculumProblemList(Long curriculumId, Long userId);
}
