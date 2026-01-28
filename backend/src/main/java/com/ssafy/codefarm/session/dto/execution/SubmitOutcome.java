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
            String expectedOutputRaw,
            String actualOutputRaw,
            String stderr,
            Boolean isTimeout,
            Boolean isOom
    ) {

        String expected = normalize(expectedOutputRaw);
        String actual = normalize(actualOutputRaw);

        LineStats stats = compareLines(expected, actual);

        if (Boolean.TRUE.equals(isTimeout)) {
            return new SubmitOutcome(
                    stats.passedCount(),
                    stats.totalCount(),
                    "시간 제한을 초과했습니다.",
                    stderr,
                    true,
                    isOom,
                    stats.failedLineNo(),
                    stats.expectedLine(),
                    stats.actualLine()
            );
        }

        if (Boolean.TRUE.equals(isOom)) {
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

        if (stderr != null && !stderr.isBlank()) {
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

        if (stats.totalCount() > 0 && stats.passedCount().equals(stats.totalCount())) {
            return new SubmitOutcome(
                    stats.totalCount(),
                    stats.totalCount(),
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null
            );
        }

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
        if (value == null) {
            return "";
        }
        return value.replace("\r\n", "\n").trim();
    }

    private static LineStats compareLines(String expected, String actual) {
        String[] e = expected.isBlank() ? new String[0] : expected.split("\n", -1);
        String[] a = actual.isBlank() ? new String[0] : actual.split("\n", -1);

        int total = e.length;
        int passed = 0;

        int maxCompare = Math.min(e.length, a.length);

        for (int i = 0; i < maxCompare; i++) {
            if (e[i].equals(a[i])) {
                passed++;
            } else {
                return LineStats.diff(total, passed, i + 1, e[i], a[i]);
            }
        }

        if (a.length < e.length && total > 0) {
            return LineStats.diff(total, passed, passed + 1, e[passed], "");
        }

        if (a.length > e.length) {
            return LineStats.diff(total, passed, total + 1, "", a[total]);
        }

        return LineStats.same(total);
    }

    private record LineStats(
            Integer totalCount,
            Integer passedCount,
            Integer failedLineNo,
            String expectedLine,
            String actualLine
    ) {
        public static LineStats diff(
                int total,
                int passed,
                int failedLineNo,
                String expectedLine,
                String actualLine
        ) {
            return new LineStats(total, passed, failedLineNo, expectedLine, actualLine);
        }

        public static LineStats same(int total) {
            return new LineStats(total, total, null, null, null);
        }
    }
}