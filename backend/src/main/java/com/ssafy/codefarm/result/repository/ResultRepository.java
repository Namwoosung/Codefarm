package com.ssafy.codefarm.result.repository;

import com.ssafy.codefarm.result.entity.Result;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ResultRepository extends JpaRepository<Result, Long> {
}
