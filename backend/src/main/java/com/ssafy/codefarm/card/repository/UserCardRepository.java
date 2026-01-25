package com.ssafy.codefarm.card.repository;

import com.ssafy.codefarm.card.entity.UserCard;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserCardRepository extends JpaRepository<UserCard, Long> {
}
