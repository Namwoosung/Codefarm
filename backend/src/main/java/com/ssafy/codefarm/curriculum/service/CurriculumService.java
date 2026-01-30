package com.ssafy.codefarm.curriculum.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumDetailQueryDto;
import com.ssafy.codefarm.curriculum.dto.query.CurriculumProblemDetailQueryDto;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumDetailResponseDto;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumProblemItemResponseDto;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumResponseDto;
import com.ssafy.codefarm.curriculum.repository.CurriculumRepository;
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
}