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
    public static SubmitOutcome from( // 실행 결과를 기반으로 제출결과 record를 생성
        SubmitContext context,
        ExecuteServerResult result
    ) {

        String expectedOutputRaw = context.problem().getTestcasesOutput();
        String actualOutputRaw = result.stdout();
        String stderr = result.stderr();
        Boolean isTimeout = result.isTimeout();
        Boolean isOom = result.isOom();

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

    private static String normalize(String value) { // 데이터 전처리(window <-> linux 호환)
        if (value == null) {
            return "";
        }
        return value.replace("\r\n", "\n").trim();
    }

    private static LineStats compareLines(String expected, String actual) { // 채점 로직, 기대값과 출력값을 라인단위로 비교하면서 정답 개수를 count
        String[] e = expected.isBlank() ? new String[0] : expected.split("\n", -1);
        String[] a = actual.isBlank() ? new String[0] : actual.split("\n", -1);

        int total = e.length;
        int maxLength = Math.max(e.length, a.length);

        int passed = 0;
        int failedLineNo = -1;
        String expectedLine = null;
        String actualLine = null;

        for (int i = 0; i < maxLength; i++) {

            String ev = i < e.length ? e[i] : "";
            String av = i < a.length ? a[i] : "";

            if (ev.equals(av)) {
                if (i < total) {
                    passed++;
                }
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

        return LineStats.diff(
            total,
            passed,
            failedLineNo,
            expectedLine,
            actualLine
        );
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