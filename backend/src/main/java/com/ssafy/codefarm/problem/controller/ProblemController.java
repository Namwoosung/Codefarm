package com.ssafy.codefarm.problem.controller;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.problem.dto.response.ProblemDetailResponseDto;
import com.ssafy.codefarm.problem.dto.response.ProblemListItemResponseDto;
import com.ssafy.codefarm.problem.dto.response.ProblemListResponseDto;
import com.ssafy.codefarm.problem.service.ProblemService;
import java.util.List;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
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

    @GetMapping("/lists")
    public SuccessResponse getProblemList(
        @RequestParam(required = false) List<Integer> difficulty,
        @RequestParam(required = false) List<String> algorithm,
        @RequestParam(defaultValue = "createdAt") String sortBy,
        @RequestParam(defaultValue = "asc") String sortDirection,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @AuthenticationPrincipal CustomUserDetails userDetails
    ) {

        if (size > 100) {
            size = 100;
        }

        Sort sort = Sort.by(Sort.Direction.fromString(sortDirection), sortBy);
        Pageable pageable = PageRequest.of(page, size, sort);

        Long userId = userDetails != null ? userDetails.getUserId() : null;

        ProblemListResponseDto responseDto =
            problemService.getProblemList(difficulty, algorithm, pageable, userId);

        return SuccessResponse.success("문제 목록 조회 성공", responseDto);
    }
}
