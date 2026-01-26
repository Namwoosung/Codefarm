package com.ssafy.codefarm.card.repository;

import com.ssafy.codefarm.card.entity.Card;
import com.ssafy.codefarm.card.entity.CardGrade;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface CardRepository extends JpaRepository<Card, Long> {

    @Query(value = "SELECT * FROM cards c WHERE c.grade = :#{#grade.name()} ORDER BY RANDOM() LIMIT 1", nativeQuery = true)
    Optional<Card> findRandomCardByGrade(@Param("grade") CardGrade grade);
}
