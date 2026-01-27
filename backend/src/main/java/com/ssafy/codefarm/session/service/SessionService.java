package com.ssafy.codefarm.session.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.problem.entity.Problem;
import com.ssafy.codefarm.problem.repository.ProblemRepository;
import com.ssafy.codefarm.result.dto.requset.SaveCodeSnapshotRequestDto;
import com.ssafy.codefarm.result.dto.response.SaveCodeSnapshotResponseDto;
import com.ssafy.codefarm.session.dto.redis.CodeSnapshotRedisDto;
import com.ssafy.codefarm.session.dto.request.CreateSessionRequestDto;
import com.ssafy.codefarm.session.dto.response.SessionResponseDto;
import com.ssafy.codefarm.session.entity.Session;
import com.ssafy.codefarm.session.entity.SessionStatus;
import com.ssafy.codefarm.session.repository.SessionRepository;
import com.ssafy.codefarm.user.entity.User;
import com.ssafy.codefarm.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class SessionService {

    private final SessionRepository sessionRepository;
    private final UserRepository userRepository;
    private final ProblemRepository problemRepository;
    private final SessionCodeRedisService sessionCodeRedisService;

    public SessionResponseDto createSession(Long userId, CreateSessionRequestDto createSessionRequestDto) {

        if (sessionRepository.existsByUserIdAndStatus(userId, SessionStatus.ACTIVE)) {
            throw new CustomException("이미 진행 중인 세션이 존재합니다.", ErrorCode.DUPLICATE_RESOURCE);
        }

        User user = userRepository.getReferenceById(userId);

        Problem problem = problemRepository.findById(createSessionRequestDto.getProblemId())
                .orElseThrow(() ->
                        new CustomException("문제를 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND)
        );

        Session session = Session.builder()
                .status(SessionStatus.ACTIVE)
                .startedAt(LocalDateTime.now())
                .user(user)
                .problem(problem)
                .build();

        try {
            sessionRepository.save(session);
        } catch (DataIntegrityViolationException e) {
            throw new CustomException(
                    "이미 진행 중인 세션이 존재합니다.",
                    ErrorCode.DUPLICATE_RESOURCE
            );
        }

        sessionCodeRedisService.initialize(session.getId());

        return SessionResponseDto.from(session);
    }

    public SessionResponseDto closeSession(Long userId, Long sessionId) {
        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        if (session.getStatus() == SessionStatus.CLOSED) {
            throw new CustomException("이미 종료된 세션입니다.", ErrorCode.BAD_REQUEST);
        }

        session.close();

        sessionCodeRedisService.delete(sessionId);

        return SessionResponseDto.from(session);
    }

    @Transactional(readOnly = true)
    public SessionResponseDto getSessionDetail(Long userId, Long sessionId) {
        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() ->
                        new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        return SessionResponseDto.from(session);
    }

    @Transactional(readOnly = true)
    public SessionResponseDto getActiveSession(Long userId) {
        Session session = sessionRepository.findByUserIdAndStatus(userId, SessionStatus.ACTIVE)
                .orElseThrow(() ->
                        new CustomException("활성 세션이 존재하지 않습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        return SessionResponseDto.from(session);
    }

    public SaveCodeSnapshotResponseDto saveCodeSnapshot(Long userId, Long sessionId, SaveCodeSnapshotRequestDto saveCodeSnapshotRequestDto) {
        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new CustomException("세션을 찾을 수 없습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if (!session.getUser().getId().equals(userId)) {
            throw new CustomException("해당 세션에 접근할 수 없습니다.", ErrorCode.FORBIDDEN);
        }

        if (session.getStatus() != SessionStatus.ACTIVE) {
            throw new CustomException("종료된 세션에는 코드를 저장할 수 없습니다.", ErrorCode.BAD_REQUEST);
        }

        LocalDateTime now = LocalDateTime.now();

        CodeSnapshotRedisDto snapshot = CodeSnapshotRedisDto.builder()
                .language(saveCodeSnapshotRequestDto.getLanguage())
                .code(saveCodeSnapshotRequestDto.getCode())
                .savedAt(now)
                .build();

        sessionCodeRedisService.appendSnapshot(sessionId, snapshot);

        return SaveCodeSnapshotResponseDto.from(now);

    }
}
