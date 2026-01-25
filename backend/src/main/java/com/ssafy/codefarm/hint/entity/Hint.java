package com.ssafy.codefarm.hint.entity;

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
        name = "hints",
        indexes = {
                @Index(name = "idx_hint_session", columnList = "session_id")
        }
)
public class Hint {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Enumerated(EnumType.STRING)
    private HintType hintType;

    @Column(columnDefinition = "TEXT")
    private String userQuestion;

    @NotNull
    @Column(columnDefinition = "TEXT")
    private String content;

    @NotNull
    @Builder.Default
    private Boolean isViewed = false;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private Session session;

    public void markAsViewed() {
        this.isViewed = true;
    }
}
