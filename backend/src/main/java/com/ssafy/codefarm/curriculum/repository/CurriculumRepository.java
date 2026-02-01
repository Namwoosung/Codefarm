package com.ssafy.codefarm.curriculum.repository;

import com.ssafy.codefarm.curriculum.entity.Curriculum;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CurriculumRepository extends JpaRepository<Curriculum, Long>, CurriculumQueryRepository {
}
