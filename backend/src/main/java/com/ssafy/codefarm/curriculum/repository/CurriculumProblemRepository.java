package com.ssafy.codefarm.curriculum.repository;

import com.ssafy.codefarm.curriculum.entity.CurriculumProblem;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CurriculumProblemRepository extends JpaRepository<CurriculumProblem, Long> {
}
