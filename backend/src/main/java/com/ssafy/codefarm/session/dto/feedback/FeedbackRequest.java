package com.ssafy.codefarm.session.dto.feedback;

import com.ssafy.codefarm.problem.entity.Problem;
import com.ssafy.codefarm.result.entity.Result;
import com.ssafy.codefarm.session.dto.redis.PreviousJudgementRedisDto;
import com.ssafy.codefarm.user.entity.User;

import java.util.Collections;
import java.util.List;
import java.util.UUID;

public record FeedbackRequest(
    String request_id,
    ProblemInfo problem,
    UserInfo user,
    CodeInfo code,
    ResultInfo result,
    List<PreviousJudgement> previous_judgement
) {

    public static FeedbackRequest of(
        Result result,
        List<PreviousJudgement> previousJudgements
    ) {
        return new FeedbackRequest(
            UUID.randomUUID().toString(),
            ProblemInfo.from(result.getSession().getProblem()),
            UserInfo.from(result.getSession().getUser()),
            new CodeInfo(
                result.getLanguage() != null ? result.getLanguage().name().toLowerCase() : null,
                result.getCode()
            ),
            ResultInfo.from(result),
            previousJudgements != null ? previousJudgements : Collections.emptyList()
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
                problem.getAlgorithm(),
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
    }

    public record ResultInfo(
        String resultType,
        Integer solveTime,
        Integer execTime,
        Integer memory
    ) {
        public static ResultInfo from(Result result) {
            return new ResultInfo(
                result.getResultType().name(),
                result.getSolveTime(),
                result.getExecTime(),
                result.getMemory()
            );
        }
    }

    public record PreviousJudgement(
        String analysis,
        String judged_at,
        List<String> mistake_type
    ) {
        public static PreviousJudgement from(PreviousJudgementRedisDto dto) {
            return new PreviousJudgement(
                dto.getAnalysis(),
                dto.getJudgedAt() != null ? dto.getJudgedAt().toString() : null,
                dto.getMistakeType()
            );
        }

        public static List<PreviousJudgement> fromList(List<PreviousJudgementRedisDto> dtos) {
            if (dtos == null || dtos.isEmpty()) {
                return Collections.emptyList();
            }
            return dtos.stream()
                    .map(PreviousJudgement::from)
                    .toList();
        }
    }
}