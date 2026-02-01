package com.ssafy.codefarm.hint.repository;

import com.ssafy.codefarm.hint.entity.Hint;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface HintRepository extends JpaRepository<Hint, Long> {
    List<Hint> findBySessionIdOrderByCreatedAtDesc(Long sessionId);
}
