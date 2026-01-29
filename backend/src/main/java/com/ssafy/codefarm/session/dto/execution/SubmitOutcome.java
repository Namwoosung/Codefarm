package com.ssafy.codefarm.session.dto.execution;

public record SubmitOutcome(
    Integer passedCount,
    Integer totalCount,
    String failReason,
    String stderr,
    Boolean isTimeout,
    Boolean isOom,
    Integer failedLineNo,
    String expectedLine,
    String actualLine
) {

    public static SubmitOutcome from(
        SubmitContext context,
        ExecuteServerResult result
    ) {

        String expected = normalize(context.problem().getTestcasesOutput());
        String actual = normalize(result.stdout());

        LineStats stats = compareLines(expected, actual);

        if (Boolean.TRUE.equals(result.isTimeout())) {
            return timeout(stats, result.stderr());
        }

        if (Boolean.TRUE.equals(result.isOom())) {
            return oom(stats, result.stderr());
        }

        if (result.stderr() != null && !result.stderr().isBlank()) {
            return runtimeError(stats, result.stderr());
        }

        if (stats.passedCount().equals(stats.totalCount())) {
            return success(stats);
        }

        return wrongAnswer(stats);
    }

    private static SubmitOutcome success(LineStats stats) {
        return new SubmitOutcome(
            stats.totalCount(),
            stats.totalCount(),
            null,
            null,
            false,
            false,
            null,
            null,
            null
        );
    }

    private static SubmitOutcome timeout(LineStats stats, String stderr) {
        return new SubmitOutcome(
            stats.passedCount(),
            stats.totalCount(),
            "시간 제한을 초과했습니다.",
            stderr,
            true,
            false,
            stats.failedLineNo(),
            stats.expectedLine(),
            stats.actualLine()
        );
    }

    private static SubmitOutcome oom(LineStats stats, String stderr) {
        return new SubmitOutcome(
            stats.passedCount(),
            stats.totalCount(),
            "메모리 제한을 초과했습니다.",
            stderr,
            false,
            true,
            stats.failedLineNo(),
            stats.expectedLine(),
            stats.actualLine()
        );
    }

    private static SubmitOutcome runtimeError(LineStats stats, String stderr) {
        return new SubmitOutcome(
            stats.passedCount(),
            stats.totalCount(),
            "런타임 오류가 발생했습니다.",
            stderr,
            false,
            false,
            stats.failedLineNo(),
            stats.expectedLine(),
            stats.actualLine()
        );
    }

    private static SubmitOutcome wrongAnswer(LineStats stats) {
        return new SubmitOutcome(
            stats.passedCount(),
            stats.totalCount(),
            "출력 결과가 일치하지 않습니다.",
            null,
            false,
            false,
            stats.failedLineNo(),
            stats.expectedLine(),
            stats.actualLine()
        );
    }

    private static String normalize(String value) {
        if (value == null) return "";
        return value.replace("\r\n", "\n").replace("\r", "\n");
    }

    private static LineStats compareLines(String expected, String actual) {
        String[] e = expected.isBlank() ? new String[0] : expected.split("\n", -1);
        String[] a = actual.isBlank() ? new String[0] : actual.split("\n", -1);

        int total = e.length;
        int max = Math.max(e.length, a.length);

        int passed = 0;
        int failedLineNo = -1;
        String expectedLine = null;
        String actualLine = null;

        for (int i = 0; i < max; i++) {

            String ev = i < e.length ? e[i] : "";
            String av = i < a.length ? a[i] : "";

            if (ev.equals(av)) {
                if (i < total) passed++;
            } else {
                if (failedLineNo == -1) {
                    failedLineNo = i + 1;
                    expectedLine = ev;
                    actualLine = av;
                }
            }
        }

        if (failedLineNo == -1) {
            return LineStats.same(total);
        }

        return LineStats.diff(total, passed, failedLineNo, expectedLine, actualLine);
    }

    private record LineStats(
        Integer totalCount,
        Integer passedCount,
        Integer failedLineNo,
        String expectedLine,
        String actualLine
    ) {

        static LineStats same(int total) {
            return new LineStats(total, total, null, null, null);
        }

        static LineStats diff(
            int total,
            int passed,
            int failedLineNo,
            String expectedLine,
            String actualLine
        ) {
            return new LineStats(total, passed, failedLineNo, expectedLine, actualLine);
        }
    }
}