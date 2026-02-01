package com.ssafy.codefarm.result.repository;

import com.ssafy.codefarm.result.entity.Result;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ResultRepository extends JpaRepository<Result, Long>, ResultQueryRepository {
    List<Result> findBySessionIdOrderByCreatedAtDesc(Long sessionId);
}
