package com.ssafy.codefarm.card.service;

import com.ssafy.codefarm.card.dto.response.DrawCardResponseDto;
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

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class CardService {
    private final CardRepository cardRepository;
    private final UserCardRepository userCardRepository;
    private final UserRepository userRepository;

    public DrawCardResponseDto drawCard(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new CustomException("유저가 존재하지 않습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if(user.getPoint() < 100){ // 카드 뽑기 포인트는 100으로 가정
            throw new CustomException("유저의 포인트가 100 미만입니다.", ErrorCode.BAD_REQUEST);
        }

        Card card = getRandomCard();

        long beforeCount =
                userCardRepository.countByUserIdAndCardId(userId, card.getId());

        UserCard userCard = UserCard.builder()
                .user(user)
                .card(card)
                .build();

        userCardRepository.save(userCard);

        user.decreasePoint(100);

        boolean isNew = beforeCount == 0;

        return DrawCardResponseDto.from(card, isNew);
    }

    private Card getRandomCard() {

        List<Card> cards = cardRepository.findAll();
        if (cards.isEmpty()) {
            throw new CustomException("카드 데이터가 없습니다.",
                    ErrorCode.RESOURCE_NOT_FOUND);
        }

        int random = ThreadLocalRandom.current().nextInt(100);

        CardGrade grade;

        if (random < 70) {
            grade = CardGrade.BRONZE;
        } else if (random < 95) {
            grade = CardGrade.SILVER;
        } else {
            grade = CardGrade.GOLD;
        }

        List<Card> filtered =
                cards.stream()
                        .filter(c -> c.getGrade() == grade)
                        .toList();

        return filtered.get(
                ThreadLocalRandom.current().nextInt(filtered.size())
        );

    }
}
