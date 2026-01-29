package com.ssafy.codefarm.problem.controller;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.problem.dto.response.ProblemDetailResponseDto;
import com.ssafy.codefarm.problem.dto.response.ProblemListItemResponseDto;
import com.ssafy.codefarm.problem.service.ProblemService;
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
@RequestMapping("/api/v1/problems")
public class ProblemController {

    private final ProblemService problemService;

    @GetMapping("/{problemId}")
    public SuccessResponse getProblemDetail(
        @PathVariable Long problemId,
        @AuthenticationPrincipal CustomUserDetails userDetails
    ) {

        Long userId = userDetails != null ? userDetails.getUserId() : null;

        ProblemDetailResponseDto problemDetailResponseDto = problemService.getProblemDetail(problemId, userId);

        return SuccessResponse.success("문제 상세 조회 성공", problemDetailResponseDto);
    }
}
