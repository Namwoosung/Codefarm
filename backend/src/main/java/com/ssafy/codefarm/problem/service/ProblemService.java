package com.ssafy.codefarm.problem.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;
import com.ssafy.codefarm.problem.dto.response.ProblemDetailResponseDto;
import com.ssafy.codefarm.problem.dto.response.ProblemListItemResponseDto;
import com.ssafy.codefarm.problem.dto.response.ProblemListResponseDto;
import com.ssafy.codefarm.problem.repository.ProblemRepository;
import java.util.List;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
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

    @Transactional(readOnly = true)
    public ProblemListResponseDto getProblemList(
        List<Integer> difficulties,
        List<String> algorithms,
        Pageable pageable,
        Long userId
    ) {

        Page<ProblemListQueryDto> page =
            problemRepository.findProblemList(
                difficulties,
                algorithms,
                pageable,
                userId
            );

        boolean isLogined = userId != null;

        List<ProblemListItemResponseDto> items =
            page.getContent()
                .stream()
                .map(dto -> ProblemListItemResponseDto.from(dto, isLogined))
                .toList();

        return new ProblemListResponseDto(
            isLogined,
            new ProblemListResponseDto.PageInfo(
                page.getNumber(),
                page.getSize(),
                page.getTotalElements(),
                page.getTotalPages()
            ),
            new ProblemListResponseDto.SortInfo(
                pageable.getSort().isEmpty()
                    ? "createdAt"
                    : pageable.getSort().iterator().next().getProperty(),
                pageable.getSort().isEmpty()
                    ? "DESC"
                    : pageable.getSort().iterator().next().getDirection().name()
            ),
            items
        );
    }
}
