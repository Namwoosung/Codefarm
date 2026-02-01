package com.ssafy.codefarm.card.repository;

import com.ssafy.codefarm.card.entity.UserCard;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface UserCardRepository extends JpaRepository<UserCard, Long> {
    boolean existsByUserIdAndCardId(Long userId, Long cardId);
    long countByUserIdAndCardId(Long userId, Long id);
}
