package com.ssafy.codefarm.card.repository;

import com.ssafy.codefarm.card.entity.Card;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CardRepository extends JpaRepository<Card, Long> {
}
