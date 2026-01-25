package com.ssafy.codefarm.result.entity;

import com.ssafy.codefarm.session.entity.Session;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Builder
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Table(
        name = "results",
        indexes = {
                @Index(name = "idx_result_session", columnList = "session_id")
        }
)
public class Result {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Enumerated(EnumType.STRING)
    private ResultType resultType;

    @NotNull
    @Column(columnDefinition = "TEXT")
    private String code;

    @NotNull
    @Enumerated(EnumType.STRING)
    private Language language;

    @NotNull
    private Integer solveTime;

    private Integer execTime;

    private Integer memory;

    @Column(columnDefinition = "TEXT")
    private String feedback;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private Session session;
}
