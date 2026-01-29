package com.ssafy.codefarm.problem.repository;

import com.ssafy.codefarm.problem.entity.Problem;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProblemRepository extends JpaRepository<Problem, Long>, ProblemQueryRepository {
}
