package com.ssafy.codefarm.result.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.result.dto.query.ReportDetailQueryDto;
import com.ssafy.codefarm.result.dto.response.ReportDetailResponseDto;
import com.ssafy.codefarm.result.repository.ResultQueryRepository;
import com.ssafy.codefarm.result.repository.ResultRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class ResultService {

    private final ResultRepository resultRepository;

    @Transactional(readOnly = true)
    public ReportDetailResponseDto getReportDetail(Long resultId, Long userId) {

        ReportDetailQueryDto dto =
                resultRepository.findReportDetail(resultId, userId);

        if (dto == null) {
            throw new CustomException("리포트를 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND);
        }

        return ReportDetailResponseDto.from(dto);
    }
}