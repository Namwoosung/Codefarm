package com.ssafy.codefarm.curriculum.entity;

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
        name = "curriculums",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_curriculum_name",
                        columnNames = {"name"}
                )
        }

)
public class Curriculum {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Column(length = 100)
    private String name;

    @NotNull
    @Column(columnDefinition = "TEXT")
    private String description;

    @NotNull
    @Enumerated(EnumType.STRING)
    private CurriculumDifficulty curriculumDifficulty;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;
}
