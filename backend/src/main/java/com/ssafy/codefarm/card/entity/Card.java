package com.ssafy.codefarm.card.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.*;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Builder
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Table(
        name = "cards",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_card_name",
                        columnNames = {"name"}
                )
        }
)
public class Card {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Column(length = 100)
    private String name;

    @NotNull
    @Enumerated(EnumType.STRING)
    private CardGrade grade;

    @NotNull
    @Column(length = 255)
    private String image;
}