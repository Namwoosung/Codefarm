package com.ssafy.codefarm.session.controller;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.result.dto.requset.SaveCodeSnapshotRequestDto;
import com.ssafy.codefarm.result.dto.response.SaveCodeSnapshotResponseDto;
import com.ssafy.codefarm.session.dto.request.CreateSessionRequestDto;
import com.ssafy.codefarm.session.dto.request.RunSessionRequestDto;
import com.ssafy.codefarm.session.dto.request.SubmitSessionRequestDto;
import com.ssafy.codefarm.session.dto.response.LatestCodeResponseDto;
import com.ssafy.codefarm.session.dto.response.RunSessionResponseDto;
import com.ssafy.codefarm.session.dto.response.SessionResponseDto;
import com.ssafy.codefarm.session.dto.response.SubmitSessionResponseDto;
import com.ssafy.codefarm.session.service.SessionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/sessions")
public class SessionController {

    private final SessionService sessionService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public SuccessResponse createSession(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @RequestBody @Valid CreateSessionRequestDto createSessionRequestDto
    ) {

        SessionResponseDto sessionResponseDto =
                sessionService.createSession(userDetails.getUserId(), createSessionRequestDto);

        return SuccessResponse.success("세션 생성 성공", sessionResponseDto);
    }

    @PatchMapping("/{sessionId}/close")
    public SuccessResponse closeSession(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @PathVariable Long sessionId
    ) {

        SessionResponseDto sessionResponseDto =
                sessionService.closeSession(userDetails.getUserId(), sessionId);

        return SuccessResponse.success("세션 종료 성공", sessionResponseDto);
    }

    @GetMapping("/{sessionId}")
    public SuccessResponse getSessionDetail(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @PathVariable Long sessionId
    ) {

        SessionResponseDto sessionResponseDto =
                sessionService.getSessionDetail(userDetails.getUserId(), sessionId);

        return SuccessResponse.success("세션 상세 조회 성공", sessionResponseDto);
    }

    @GetMapping("/active")
    public SuccessResponse getActiveSession(
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {

        SessionResponseDto sessionResponseDto =
                sessionService.getActiveSession(userDetails.getUserId());

        return SuccessResponse.success("활성 세션 조회 성공", sessionResponseDto);
    }

    @PostMapping("/{sessionId}/codes")
    @ResponseStatus(HttpStatus.CREATED)
    public SuccessResponse saveCodeSnapshot(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @PathVariable Long sessionId,
            @RequestBody @Valid SaveCodeSnapshotRequestDto saveCodeSnapshotRequestDto
    ) {

        SaveCodeSnapshotResponseDto saveCodeSnapshotResponseDto =
                sessionService.saveCodeSnapshot(userDetails.getUserId(), sessionId, saveCodeSnapshotRequestDto);

        return SuccessResponse.success("코드 스냅샷 저장 성공", saveCodeSnapshotResponseDto);
    }

    @GetMapping("/{sessionId}/codes/latest")
    @ResponseStatus(HttpStatus.OK)
    public SuccessResponse getLatestCode(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @PathVariable Long sessionId
    ) {

        LatestCodeResponseDto latestCodeResponseDto = sessionService.getLatestCode(userDetails.getUserId(), sessionId);

        return SuccessResponse.success("최신 코드 조회 성공", latestCodeResponseDto);
    }


    // 동기 처리로 변경
    @PostMapping("/{sessionId}/run")
    @ResponseStatus(HttpStatus.OK)
    public SuccessResponse runSession(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @PathVariable Long sessionId,
            @RequestBody @Valid RunSessionRequestDto requestDto
    ) {

        RunSessionResponseDto result = sessionService.runSession(sessionId, userDetails.getUserId(), requestDto);

        String message = (result.stderr() == null || result.stderr().isBlank())
                ? "실행 완료"
                : "실행 실패";

        return SuccessResponse.success(message, result);
    }


    @PostMapping("/{sessionId}/submit")
    @ResponseStatus(HttpStatus.OK)
    public SuccessResponse submitSession(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @PathVariable Long sessionId,
            @RequestBody @Valid SubmitSessionRequestDto submitSessionRequestDto
    ) {

        SubmitSessionResponseDto result =
                sessionService.submitSession(
                        userDetails.getUserId(),
                        sessionId,
                        submitSessionRequestDto
                );

        String message = result.resultType() == com.ssafy.codefarm.result.entity.ResultType.SUCCESS
                ? "제출에 성공했습니다."
                : "제출에 실패했습니다.";

        return SuccessResponse.success(message, result);
    }
}
