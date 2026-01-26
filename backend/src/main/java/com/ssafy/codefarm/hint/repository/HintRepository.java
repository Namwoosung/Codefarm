package com.ssafy.codefarm.hint.repository;

import com.ssafy.codefarm.hint.entity.Hint;
import org.springframework.data.jpa.repository.JpaRepository;

public interface HintRepository extends JpaRepository<Hint, Long> {
}
