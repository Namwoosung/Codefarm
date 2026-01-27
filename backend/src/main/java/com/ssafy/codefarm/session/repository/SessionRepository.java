package com.ssafy.codefarm.session.repository;

import com.ssafy.codefarm.session.entity.Session;
import com.ssafy.codefarm.session.entity.SessionStatus;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SessionRepository extends JpaRepository<Session, Long> {
    boolean existsByUserIdAndStatus(Long userId, SessionStatus status);
}
