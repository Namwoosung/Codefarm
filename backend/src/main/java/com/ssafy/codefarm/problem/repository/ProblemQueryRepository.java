package com.ssafy.codefarm.problem.repository;

import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface ProblemQueryRepository {

    ProblemListQueryDto findProblemDetail(Long problemId, Long userId);

    Page<ProblemListQueryDto> findProblemList(
        List<Integer> difficulties,
        List<String> algorithms,
        Pageable pageable, Long userId
    );
}
