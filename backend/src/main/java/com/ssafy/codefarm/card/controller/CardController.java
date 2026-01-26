package com.ssafy.codefarm.card.controller;

import com.ssafy.codefarm.card.dto.response.DrawCardResponseDto;
import com.ssafy.codefarm.card.service.CardService;
import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/cards")
public class CardController {
    private final CardService cardService;

    @PostMapping("/draw")
    @ResponseStatus(HttpStatus.CREATED)
    public SuccessResponse drawCard(
            @AuthenticationPrincipal CustomUserDetails userDetails
    ){
        DrawCardResponseDto drawCardResponseDto =
                cardService.drawCard(userDetails.getUserId());

        return SuccessResponse.success("카드 뽑기 성공", drawCardResponseDto);
    }
}
