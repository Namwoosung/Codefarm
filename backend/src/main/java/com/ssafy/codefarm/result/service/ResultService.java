package com.ssafy.codefarm.result.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.result.dto.query.ReportDetailQueryDto;
import com.ssafy.codefarm.result.dto.response.ReportDetailResponseDto;
import com.ssafy.codefarm.result.dto.response.ResultMyReportListResponseDto;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.result.repository.ResultRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

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

    @Transactional(readOnly = true)
    public ResultMyReportListResponseDto getMyReportList(
            ResultType resultType, String sortBy, String sortDirection, int page, int size, Long userId
    ) {

        // resultType은 SUCCESS/GIVE_UP만 허용 (선택)
        if (resultType != null
                && resultType != ResultType.SUCCESS
                && resultType != ResultType.GIVE_UP) {
            throw new CustomException("잘못된 resultType 입니다.", ErrorCode.INVALID_PARAMETER);
        }

        // sortBy는 createdAt만 허용
        if (sortBy == null || sortBy.isBlank()) {
            sortBy = "createdAt";
        }
        if (!sortBy.equals("createdAt")) {
            throw new CustomException("정렬 기준이 올바르지 않습니다.", ErrorCode.INVALID_PARAMETER);
        }

        // sortDirection 기본 desc, asc/desc 외 거부
        Sort.Direction direction;
        try {
            direction = Sort.Direction.fromString(sortDirection == null ? "desc" : sortDirection);
        } catch (IllegalArgumentException e) {
            throw new CustomException("정렬 방향이 올바르지 않습니다.", ErrorCode.INVALID_PARAMETER);
        }

        Sort sort = Sort.by(direction, sortBy);
        Pageable pageable = PageRequest.of(page, size, sort);

        Page<ReportDetailQueryDto> resultPage =
                resultRepository.findMyReportList(userId, resultType, pageable);

        List<ReportDetailResponseDto> items =
                resultPage.getContent().stream()
                        .map(ReportDetailResponseDto::from)
                        .toList();

        return new ResultMyReportListResponseDto(
                new ResultMyReportListResponseDto.PageInfo(
                        resultPage.getNumber(),
                        resultPage.getSize(),
                        resultPage.getTotalElements(),
                        resultPage.getTotalPages()
                ),
                new ResultMyReportListResponseDto.SortInfo(
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