package com.ssafy.codefarm.problem.entity;

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
@Table(name = "problems")
public class Problem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    private String title;

    @NotNull
    @Column(columnDefinition = "TEXT")
    private String description;

    @NotNull
    @Column(columnDefinition = "TEXT")
    private String inputDescription;

    @NotNull
    @Column(columnDefinition = "TEXT")
    private String outputDescription;

    @NotNull
    @Enumerated(EnumType.STRING)
    private ProblemDifficulty difficulty;

    @NotNull
    @Enumerated(EnumType.STRING)
    private AlgorithmType algorithm;

    @NotNull
    private Integer timeLimit;

    @NotNull
    private Integer memoryLimit;

    @NotNull
    @Column(columnDefinition = "TEXT")
    private String exampleInput;

    @NotNull
    @Column(columnDefinition = "TEXT")
    private String exampleOutput;

    @NotNull
    @Column(columnDefinition = "TEXT")
    private String testcasesInput;

    @NotNull
    @Column( columnDefinition = "TEXT")
    private String testcasesOutput;

    @NotNull
    @Enumerated(EnumType.STRING)
    private ProblemType problemType;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;
}