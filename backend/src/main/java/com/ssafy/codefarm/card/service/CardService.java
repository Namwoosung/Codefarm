package com.ssafy.codefarm.card.service;

import com.ssafy.codefarm.card.dto.query.MyCardQueryDto;
import com.ssafy.codefarm.card.dto.response.CardDetailResponseDto;
import com.ssafy.codefarm.card.dto.response.CardSummaryResponseDto;
import com.ssafy.codefarm.card.dto.response.DrawCardResponseDto;
import com.ssafy.codefarm.card.dto.response.MyCardListResponseDto;
import com.ssafy.codefarm.card.entity.Card;
import com.ssafy.codefarm.card.entity.CardGrade;
import com.ssafy.codefarm.card.entity.UserCard;
import com.ssafy.codefarm.card.repository.CardRepository;
import com.ssafy.codefarm.card.repository.UserCardRepository;
import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.user.entity.User;
import com.ssafy.codefarm.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class CardService {
    private static final int DRAW_COST = 100;

    private final CardRepository cardRepository;
    private final UserCardRepository userCardRepository;
    private final UserRepository userRepository;

    public DrawCardResponseDto drawCard(Long userId) {

        // 포인트 차감 (Atomic Update) - 동시성 제어
        int updatedRows = userRepository.decreasePointIfEnough(userId, DRAW_COST);
        if (updatedRows == 0) {
            throw new CustomException("포인트가 부족합니다.", ErrorCode.BAD_REQUEST);
        }

        // 랜덤 등급 선택
        CardGrade randomGrade = CardGrade.pickRandom();

        // 해당 등급의 카드 중 랜덤 1장 조회
        Card card = cardRepository.findRandomCardByGrade(randomGrade)
                .orElseThrow(() -> new CustomException("해당 등급의 카드가 존재하지 않습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        // 유저-카드 매핑 저장
        User user = userRepository.getReferenceById(userId); // 프록시만 조회

        boolean isNew = !userCardRepository.existsByUserIdAndCardId(userId, card.getId());

        UserCard userCard = UserCard.builder()
                .user(user)
                .card(card)
                .build();

        userCardRepository.save(userCard);

        return DrawCardResponseDto.from(card, isNew);
    }

    @Transactional(readOnly = true)
    public MyCardListResponseDto getMyCards(Long userId) {
        List<MyCardQueryDto> myCards = cardRepository.findMyCards(userId);

        long totalMyCard = myCards.size();
        long totalServiceCard = cardRepository.count();

        Map<String, Long> gradeCounts = myCards.stream()
                .collect(Collectors.groupingBy(
                        dto -> dto.grade().name(),
                        Collectors.counting()
                ));

        CardSummaryResponseDto summary = new CardSummaryResponseDto(
                totalMyCard,
                totalServiceCard,
                gradeCounts
        );

        return MyCardListResponseDto.from(summary, myCards);
    }

    @Transactional(readOnly = true)
    public CardDetailResponseDto getCardDetail(Long cardId, Long userId) {
        Card card = cardRepository.findById(cardId)
                .orElseThrow(() ->
                        new CustomException(
                                "카드를 찾을 수 없습니다.",
                                ErrorCode.RESOURCE_NOT_FOUND
                        )
                );

        long count = userCardRepository
                .countByUserIdAndCardId(userId, cardId);

        List<LocalDateTime> history =
                cardRepository.findAcquiredHistory(userId, cardId);

        return CardDetailResponseDto.from(card, count, history);
    }
}
