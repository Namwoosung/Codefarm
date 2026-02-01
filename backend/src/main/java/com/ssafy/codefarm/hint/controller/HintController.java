package com.ssafy.codefarm.hint.controller;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.hint.dto.requset.ManualHintRequestDto;
import com.ssafy.codefarm.hint.service.HintService;
import com.ssafy.codefarm.result.dto.response.ManualHintResponseDto;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/sessions")
public class HintController {

    private final HintService hintService;

    @GetMapping(value = "/{sessionId}/hints/subscribe", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter subscribeAutoHint(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @PathVariable Long sessionId
    ) {
        return hintService.subscribe(sessionId, userDetails.getUserId());
    }

    @PostMapping("/{sessionId}/hints/manual")
    @ResponseStatus(HttpStatus.CREATED)
    public SuccessResponse createManualHint(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @PathVariable Long sessionId,
            @RequestBody @Valid ManualHintRequestDto requestDto
    ) {

        ManualHintResponseDto manualHintResponseDto =
                hintService.createManualHint(sessionId, userDetails.getUserId(), requestDto);

        return SuccessResponse.success("힌트 생성 성공", manualHintResponseDto);
    }
}
