package com.ssafy.codefarm.card.controller;

import com.ssafy.codefarm.card.dto.response.CardDetailResponseDto;
import com.ssafy.codefarm.card.dto.response.CardRankingResponseDto;
import com.ssafy.codefarm.card.dto.response.DrawCardResponseDto;
import com.ssafy.codefarm.card.dto.response.MyCardListResponseDto;
import com.ssafy.codefarm.card.service.CardService;
import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

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

    @GetMapping("/me")
    @ResponseStatus(HttpStatus.OK)
    public SuccessResponse getMyCards(
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {
        MyCardListResponseDto myCardListResponseDto =
                cardService.getMyCards(userDetails.getUserId());

        return SuccessResponse.success("내 카드 목록 조회 성공", myCardListResponseDto);
    }

    @GetMapping("/{cardId}")
    @ResponseStatus(HttpStatus.OK)
    public SuccessResponse getCardDetail(
            @PathVariable Long cardId,
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {

        CardDetailResponseDto cardDetailResponseDto =
                cardService.getCardDetail(
                        cardId,
                        userDetails.getUserId()
                );

        return SuccessResponse.success(
                "카드 상세 조회 성공",
                cardDetailResponseDto
        );
    }

    @GetMapping("/rankings")
    public SuccessResponse getCardRankings() {

        CardRankingResponseDto response =
                cardService.getCardRankings();

        return SuccessResponse.success("카드 랭킹 조회 성공", response);
    }
}
