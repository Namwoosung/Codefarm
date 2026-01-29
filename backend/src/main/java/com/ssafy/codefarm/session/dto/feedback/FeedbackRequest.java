package com.ssafy.codefarm.session.dto.feedback;

import com.ssafy.codefarm.problem.entity.Problem;
import com.ssafy.codefarm.session.dto.execution.SubmitContext;
import com.ssafy.codefarm.session.dto.request.SubmitSessionRequestDto;
import com.ssafy.codefarm.user.entity.User;
import java.util.UUID;

public record FeedbackRequest(
    String request_id,
    ProblemInfo problem,
    UserInfo user,
    CodeInfo code
) {

    public static FeedbackRequest from(
        SubmitContext context,
        SubmitSessionRequestDto dto
    ) {

        return new FeedbackRequest(
            UUID.randomUUID().toString(),
            ProblemInfo.from(context.problem()),
            UserInfo.from(context.session().getUser()),
            CodeInfo.from(dto)
        );
    }

    public record ProblemInfo(
        String title,
        String description,
        String input_description,
        String output_description,
        Integer difficulty,
        String algorithm,
        Double time_limit,
        Integer memory_limit
    ) {
        public static ProblemInfo from(Problem problem) {
            return new ProblemInfo(
                problem.getTitle(),
                problem.getDescription(),
                problem.getInputDescription(),
                problem.getOutputDescription(),
                problem.getDifficulty(),
                problem.getAlgorithm().name(),
                (double) problem.getTimeLimit(),
                problem.getMemoryLimit()
            );
        }
    }

    public record UserInfo(
        Long id,
        Integer coding_level,
        Integer age
    ) {
        public static UserInfo from(User user) {
            return new UserInfo(
                user.getId(),
                user.getCodingLevel(),
                user.getAge()
            );
        }
    }

    public record CodeInfo(
        String language,
        String content
    ) {
        public static CodeInfo from(SubmitSessionRequestDto dto) {
            return new CodeInfo(
                dto.getLanguage().name().toLowerCase(),
                dto.getCode()
            );
        }
    }
}