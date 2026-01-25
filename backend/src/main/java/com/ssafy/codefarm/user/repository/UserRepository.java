package com.ssafy.codefarm.user.repository;

import com.ssafy.codefarm.user.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
}
