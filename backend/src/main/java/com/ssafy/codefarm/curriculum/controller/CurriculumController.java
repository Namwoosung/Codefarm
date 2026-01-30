package com.ssafy.codefarm.curriculum.controller;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumDetailResponseDto;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumListResponseDto;
import com.ssafy.codefarm.curriculum.dto.response.CurriculumRecommendResponseDto;
import com.ssafy.codefarm.curriculum.service.CurriculumService;
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
@RequestMapping("/api/v1/curriculums")
public class CurriculumController {

    private final CurriculumService curriculumService;

    @GetMapping("/{curriculumId}")
    public SuccessResponse getCurriculumDetail(
            @PathVariable Long curriculumId,
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {
        Long userId = userDetails != null ? userDetails.getUserId() : null;

        CurriculumDetailResponseDto responseDto =
                curriculumService.getCurriculumDetail(curriculumId, userId);

        return SuccessResponse.success("커리큘럼 상세 조회 성공", responseDto);
    }

    @GetMapping("/{curriculumId}/recommend")
    public SuccessResponse getRecommendedProblem(
            @PathVariable Long curriculumId,
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {

        CurriculumRecommendResponseDto curriculumRecommendResponseDto =
                curriculumService.getRecommendedProblem(curriculumId, userDetails.getUserId());

        return SuccessResponse.success("커리큘럼 추천 문제 조회 성공", curriculumRecommendResponseDto);
    }

    @GetMapping("/lists")
    public SuccessResponse getCurriculumList(
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {

        Long userId = userDetails != null ? userDetails.getUserId() : null;

        CurriculumListResponseDto responseDto =
                curriculumService.getCurriculumList(userId);

        return SuccessResponse.success("커리큘럼 목록 조회 성공", responseDto);
    }
}