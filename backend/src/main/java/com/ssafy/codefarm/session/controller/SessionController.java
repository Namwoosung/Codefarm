package com.ssafy.codefarm.session.controller;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.session.dto.request.CreateSessionRequestDto;
import com.ssafy.codefarm.session.dto.response.SessionResponseDto;
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
}
