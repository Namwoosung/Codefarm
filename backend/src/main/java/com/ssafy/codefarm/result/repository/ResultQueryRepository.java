package com.ssafy.codefarm.result.repository;

import com.ssafy.codefarm.result.dto.query.ReportDetailQueryDto;

public interface ResultQueryRepository {
    ReportDetailQueryDto findReportDetail(Long resultId, Long userId);

}
