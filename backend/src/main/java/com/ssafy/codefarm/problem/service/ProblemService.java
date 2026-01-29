package com.ssafy.codefarm.problem.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;
import com.ssafy.codefarm.problem.dto.response.ProblemDetailResponseDto;
import com.ssafy.codefarm.problem.dto.response.ProblemListItemResponseDto;
import com.ssafy.codefarm.problem.repository.ProblemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class ProblemService {
    private final ProblemRepository problemRepository;


    @Transactional(readOnly = true)
    public ProblemDetailResponseDto getProblemDetail(Long problemId, Long userId) {
        ProblemListQueryDto dto = problemRepository.findProblemDetail(problemId, userId);

        if (dto == null) {
            throw new CustomException("문제를 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND);
        }

        boolean isLogined = userId != null;

        ProblemListItemResponseDto item =
            ProblemListItemResponseDto.from(dto, isLogined);

        return ProblemDetailResponseDto.from(item, isLogined);

    }
}
