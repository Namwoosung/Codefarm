package com.ssafy.codefarm.hint.dto.ai;

import java.util.List;

public record AIHintResponse(
        CurrentJudgement current_judgement,
        String hint
) {

    public record CurrentJudgement(
            String judged_at,
            List<String> mistake_type,
            String analysis
    ) {}
}