package com.ssafy.codefarm.hint.dto.ai;

import com.ssafy.codefarm.problem.entity.Problem;
import com.ssafy.codefarm.session.dto.redis.CodeSnapshotRedisDto;
import com.ssafy.codefarm.session.dto.redis.PreviousJudgementRedisDto;
import com.ssafy.codefarm.session.entity.Session;
import com.ssafy.codefarm.user.entity.User;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Comparator;
import java.util.List;

public record AIHintRequest(

        String started_at,
        String observed_at,
        String language,
        String user_question,
        UserInformation user_information,
        ProblemInformation problem_information,
        List<CodeHistoryItem> code_history,
        List<PreviousJudgementItem> previous_judgement
) {

    public static AIHintRequest of(
            Session session,
            User user,
            Problem problem,
            String userQuestion,
            List<CodeSnapshotRedisDto> snapshots,
            List<PreviousJudgementRedisDto> previousJudgements
    ) {

        List<CodeHistoryItem> filteredHistory = filterCodeHistory(snapshots);

        return new AIHintRequest(
                session.getStartedAt().atOffset(ZoneOffset.UTC).toString(), // 이거 타임존 꼬이면 다시 제시
                OffsetDateTime.now(ZoneOffset.UTC).toString(),
                extractLanguage(filteredHistory),
                userQuestion,
                UserInformation.from(user),
                ProblemInformation.from(problem),
                filteredHistory,
                PreviousJudgementItem.fromList(previousJudgements)
        );
    }


    // 최근 5분 이내 snapshot만 포함, 없으면 가장 최근 snapshot 1개만 포함
    private static List<CodeHistoryItem> filterCodeHistory(List<CodeSnapshotRedisDto> snapshots) {

        if (snapshots == null || snapshots.isEmpty()) {
            return List.of();
        }

        LocalDateTime now = LocalDateTime.now();
        LocalDateTime fiveMinutesAgo = now.minusMinutes(5);

        // 최근 5분 이내
        List<CodeHistoryItem> recent = snapshots.stream()
                .filter(dto -> dto.getSavedAt().isAfter(fiveMinutesAgo))
                .sorted(Comparator.comparing(CodeSnapshotRedisDto::getSavedAt))
                .map(dto -> new CodeHistoryItem(
                        dto.getCode(),
                        dto.getSavedAt().atOffset(ZoneOffset.UTC).toString()
                ))
                .toList();

        if (!recent.isEmpty()) {
            return recent;
        }

        // 최근 5분 이내 없으면 가장 최근 1개
        CodeSnapshotRedisDto latest = snapshots.stream()
                .max(Comparator.comparing(CodeSnapshotRedisDto::getSavedAt))
                .orElse(null);

        if (latest == null) {
            return List.of();
        }

        return List.of(
                new CodeHistoryItem(
                        latest.getCode(),
                        latest.getSavedAt().atOffset(ZoneOffset.UTC).toString()
                )
        );
    }

    private static String extractLanguage(List<CodeHistoryItem> history) {
//        if (history == null || history.isEmpty()) return null;
//        return history.get(history.size() - 1).code() != null ? "python" : null;
        return "python"; // 현재는 python만 호환 가능
    }

    public record UserInformation(
            Integer age,
            Integer coding_level,
            String user_id
    ) {
        public static UserInformation from(User user) {
            return new UserInformation(
                    user.getAge(),
                    user.getCodingLevel(),
                    String.valueOf(user.getId())
            );
        }
    }

    public record ProblemInformation(
            String algorithm,
            String description,
            Integer difficulty,
            String problem_id
    ) {
        public static ProblemInformation from(Problem problem) {
            return new ProblemInformation(
                    problem.getAlgorithm(),
                    problem.getDescription(),
                    problem.getDifficulty(),
                    String.valueOf(problem.getId())
            );
        }
    }

    public record CodeHistoryItem(
            String code,
            String timestamp
    ) {}

    public record PreviousJudgementItem(
            String analysis,
            String judged_at,
            List<String> mistake_type,
            String hint
    ) {
        public static List<PreviousJudgementItem> fromList(List<PreviousJudgementRedisDto> list) {
            if (list == null) return List.of();
            return list.stream()
                    .map(dto -> new PreviousJudgementItem(
                            dto.getAnalysis(),
                            dto.getJudgedAt() != null
                                    ? dto.getJudgedAt().atOffset(ZoneOffset.UTC).toString()
                                    : null,
                            dto.getMistakeType(),
                            dto.getHint()
                    ))
                    .toList();
        }
    }
}