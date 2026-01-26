package com.ssafy.codefarm.session.entity;

import com.ssafy.codefarm.problem.entity.Problem;
import com.ssafy.codefarm.user.entity.User;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.*;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Builder
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Table(name = "sessions")
public class Session {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Enumerated(EnumType.STRING)
    private SessionStatus status;

    @NotNull
    private LocalDateTime startedAt;

    private LocalDateTime endedAt;

    @NotNull
    @Builder.Default
    private Integer maxHint = 3;

    @NotNull
    @Builder.Default
    private Integer usedHint = 0;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private User user;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "problem_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private Problem problem;

    public void close() {
        this.status = SessionStatus.CLOSED;
        this.endedAt = LocalDateTime.now();
    }

    public void increaseHint() {
        this.usedHint++;
    }
}
