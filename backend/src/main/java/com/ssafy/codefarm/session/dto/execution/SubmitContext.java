package com.ssafy.codefarm.session.dto.execution;

import com.ssafy.codefarm.problem.entity.Problem;
import com.ssafy.codefarm.session.entity.Session;

public record SubmitContext(
        Session session,
        Problem problem,
        Integer solveTime
) {
}