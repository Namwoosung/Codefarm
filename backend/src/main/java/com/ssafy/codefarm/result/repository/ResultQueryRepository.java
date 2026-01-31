package com.ssafy.codefarm.result.repository;

import com.ssafy.codefarm.result.dto.query.ReportDetailQueryDto;
import com.ssafy.codefarm.result.entity.ResultType;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface ResultQueryRepository {
    ReportDetailQueryDto findReportDetail(Long resultId, Long userId);

    Page<ReportDetailQueryDto> findMyReportList(Long userId, ResultType resultType, Pageable pageable);

}
