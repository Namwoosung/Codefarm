package com.ssafy.codefarm.user.repository;

import com.ssafy.codefarm.user.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);

    boolean existsByEmail(String email);

    boolean existsByNickname(String nickname);

    @Modifying(clearAutomatically = true)
    @Query("""
        UPDATE User u
        SET u.point = u.point - :amount
        WHERE u.id = :userId
        AND u.point >= :amount
    """)
    int decreasePointIfEnough(
            @Param("userId") Long userId,
            @Param("amount") int amount
    );
}
