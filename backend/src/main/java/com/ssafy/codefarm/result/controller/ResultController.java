package com.ssafy.codefarm.result.controller;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.result.dto.response.ReportDetailResponseDto;
import com.ssafy.codefarm.result.dto.response.ResultMyReportListResponseDto;
import com.ssafy.codefarm.result.entity.ResultType;
import com.ssafy.codefarm.result.service.ResultService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

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

    @GetMapping("/me")
    public SuccessResponse getMyReportList(
            @RequestParam(required = false) ResultType resultType,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "desc") String sortDirection,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {
        if (size > 100) {
            size = 100;
        }

        Sort sort = Sort.by(Sort.Direction.fromString(sortDirection), sortBy);
        Pageable pageable = PageRequest.of(page, size, sort);

        ResultMyReportListResponseDto responseDto =
                resultService.getMyReportList(resultType, sortBy, sortDirection, page, size, userDetails.getUserId());

        return SuccessResponse.success("내 리포트 목록 조회 성공", responseDto);
    }
}
