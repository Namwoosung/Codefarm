package com.ssafy.codefarm.user.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Builder
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Table(
        name = "users",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_user_email",
                        columnNames = {"email"}
                ),
                @UniqueConstraint(
                        name = "uk_user_nickname",
                        columnNames = {"nickname"}
                )
        }
)
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Column(length = 255)
    private String email;

    @NotNull
    @Column(length = 255)
    private String password;

    @NotNull
    @Column(length = 50)
    private String name;

    @NotNull
    @Column(length = 50)
    private String nickname;

    @NotNull
    private Integer age;

    @NotNull
    private Integer codingLevel;

    @NotNull
    @Builder.Default
    private Integer point = 0;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;

    public void updateProfile(String name, String nickname, Integer age) {
        this.name = name;
        this.nickname = nickname;
        this.age = age;
    }

    public void updateCodingLevel(Integer level) {
        this.codingLevel = level;
    }

    public void increasePoint(Integer amount) {
        this.point += amount;
    }

    public void decreasePoint(Integer amount) {
        this.point -= amount;
    }

    public void changePassword(String password) {
        this.password = password;
    }
}
