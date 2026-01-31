package com.ssafy.codefarm.result.controller;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.result.dto.response.ReportDetailResponseDto;
import com.ssafy.codefarm.result.service.ResultService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/reports")
public class ResultController {

    private final ResultService resultService;

    @GetMapping("/{reportId}")
    public SuccessResponse getReportDetail(
            @PathVariable Long reportId,
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {

        Long userId = userDetails.getUserId();

        ReportDetailResponseDto responseDto =
                resultService.getReportDetail(reportId, userId);

        return SuccessResponse.success("리포트 상세 조회 성공", responseDto);
    }
}
