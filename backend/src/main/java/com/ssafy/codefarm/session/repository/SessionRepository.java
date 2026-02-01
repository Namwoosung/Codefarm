package com.ssafy.codefarm.session.repository;

import com.ssafy.codefarm.session.entity.Session;
import com.ssafy.codefarm.session.entity.SessionStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface SessionRepository extends JpaRepository<Session, Long> {
    boolean existsByUserIdAndStatus(Long userId, SessionStatus status);

    Optional<Session> findByUserIdAndStatus(Long userId, SessionStatus status);
}
