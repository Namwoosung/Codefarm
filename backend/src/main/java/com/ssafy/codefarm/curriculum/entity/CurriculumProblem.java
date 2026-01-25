package com.ssafy.codefarm.curriculum.entity;

import com.ssafy.codefarm.problem.entity.Problem;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.*;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Builder
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Table(
        name = "curriculum_problems",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_curriculum_problem",
                        columnNames = {"curriculum_id", "problem_id"}
                ),
                @UniqueConstraint(
                        name = "uk_curriculum_order",
                        columnNames = {"curriculum_id", "order_no"}
                )
        },
        indexes = {
                @Index(
                        name = "idx_curriculum_order",
                        columnList = "curriculum_id, order_no"
                )
        }
)
public class CurriculumProblem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    private Integer orderNo;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "curriculum_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private Curriculum curriculum;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "problem_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private Problem problem;
}
