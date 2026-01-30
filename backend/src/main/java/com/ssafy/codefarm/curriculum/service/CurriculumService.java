package com.ssafy.codefarm.curriculum.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumDetailQueryDto;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumProblemDetailQueryDto;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumProblemOrderDto;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumDetailResponseDto;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumProblemItemResponseDto;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumRecommendResponseDto;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumResponseDto;
import com.ssafy.codefarm.curriculum.entity.Curriculum;
import com.ssafy.codefarm.curriculum.repository.CurriculumRepository;
import com.ssafy.codefarm.problem.dto.query.ProblemListQueryDto;
import com.ssafy.codefarm.problem.dto.response.ProblemListItemResponseDto;
import com.ssafy.codefarm.problem.repository.ProblemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class CurriculumService {

    private final CurriculumRepository curriculumRepository;
    private final ProblemRepository problemRepository;

    @Transactional(readOnly = true)
    public CurriculumDetailResponseDto getCurriculumDetail(Long curriculumId, Long userId) {

        CurriculumDetailQueryDto curriculumDto =
                curriculumRepository.findCurriculumDetail(curriculumId);

        if (curriculumDto == null) {
            throw new CustomException("커리큘럼을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND);
        }

        boolean isLogined = userId != null;

        List<CurriculumProblemDetailQueryDto> problemDtos =
                curriculumRepository.findCurriculumProblemList(curriculumId, userId);

        List<CurriculumProblemItemResponseDto> problems =
                problemDtos.stream()
                        .map(dto -> CurriculumProblemItemResponseDto.from(dto, isLogined))
                        .toList();

        Integer solvedProblemCount = null;
        if (isLogined) {
            solvedProblemCount = (int) problemDtos.stream()
                    .filter(dto -> Boolean.TRUE.equals(dto.isSolved()))
                    .count();
        }

        CurriculumResponseDto curriculumResponseDto =
                CurriculumResponseDto.from(curriculumDto, solvedProblemCount, problems);

        return CurriculumDetailResponseDto.from(isLogined, curriculumResponseDto);
    }

    @Transactional(readOnly = true)
    public CurriculumRecommendResponseDto getRecommendedProblem(
            Long curriculumId,
            Long userId
    ) {

        Curriculum curriculum = curriculumRepository.findById(curriculumId)
                .orElseThrow(() -> new CustomException("커리큘럼을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if (curriculum.getCurriculumDifficulty() < 4) {
            throw new CustomException("추천 문제는 난이도 4 이상 커리큘럼에서만 제공합니다.", ErrorCode.BAD_REQUEST);
        }

        List<CurriculumProblemOrderDto> problems =
                curriculumRepository.findCurriculumProblemOrders(curriculumId, userId);

        CurriculumProblemOrderDto blocked = problems.stream()
                .filter(p -> !Boolean.TRUE.equals(p.isSolved()))
                .findFirst()
                .orElse(null);

        if (blocked == null) {
            return new CurriculumRecommendResponseDto(true, null);
        }

        ProblemListQueryDto recommended =
                curriculumRepository.findRandomRecommendedProblem(
                        blocked.algorithm(),
                        blocked.difficulty(),
                        userId
                );

        if (recommended == null) {
            return new CurriculumRecommendResponseDto(true, null);
        }

        ProblemListItemResponseDto item = ProblemListItemResponseDto.from(recommended, true);

        return new CurriculumRecommendResponseDto(true, item);
    }
}