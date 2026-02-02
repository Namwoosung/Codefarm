package com.ssafy.codefarm.user.service;

import com.ssafy.codefarm.common.authority.JwtTokenProvider;
import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.LoginTokenResult;
import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.user.dto.request.*;
import com.ssafy.codefarm.user.dto.response.*;
import com.ssafy.codefarm.user.entity.User;
import com.ssafy.codefarm.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class UserService {
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;

    private final RefreshTokenRedisService refreshTokenRedisService;

    private final UserRepository userRepository;

    public UserResponseDto signup(UserSignupRequestDto userSignupRequestDto) {
        if (userRepository.existsByEmail(userSignupRequestDto.getEmail())) {
            throw new CustomException(
                    "이미 사용 중인 이메일입니다.",
                    ErrorCode.DUPLICATE_RESOURCE
            );
        }

        if (userRepository.existsByNickname(userSignupRequestDto.getNickname())) {
            throw new CustomException(
                    "이미 사용 중인 닉네임입니다.",
                    ErrorCode.DUPLICATE_RESOURCE
            );
        }

        User user = User.builder()
                .email(userSignupRequestDto.getEmail())
                .password(passwordEncoder.encode(userSignupRequestDto.getPassword()))
                .name(userSignupRequestDto.getName())
                .nickname(userSignupRequestDto.getNickname())
                .age(userSignupRequestDto.getAge())
                .codingLevel(userSignupRequestDto.getCodingLevel())
                .point(0)
                .build();

        userRepository.save(user);

        return UserResponseDto.from(user);
    }

    @Transactional(readOnly = true)
    public CheckEmailResponseDto checkEmailDuplicate(CheckEmailRequestDto checkEmailRequestDto) {
        return new CheckEmailResponseDto(!userRepository.existsByEmail(checkEmailRequestDto.getEmail()));
    }

    @Transactional(readOnly = true)
    public CheckNicknameResponseDto checkNicknameDuplicate(CheckNicknameRequestDto checkNicknameRequestDto) {
        return new CheckNicknameResponseDto(!userRepository.existsByNickname(checkNicknameRequestDto.getNickname()));
    }

    @Transactional(readOnly = true)
    public LoginTokenResult login(LoginRequestDto loginRequestDto) {
        //인증을 위한 UsernamePasswordAuthenticationToken을 생성
        UsernamePasswordAuthenticationToken authenticate
                = new UsernamePasswordAuthenticationToken(loginRequestDto.getEmail(), loginRequestDto.getPassword());

        //spring security를 통해 인증 수행 => authenticationManager에게 생성한 토큰 인증을 요구, 인증 완료 후 결과를 Authentication으로 받음
        Authentication authentication;
        try {
            authentication =
                    authenticationManager.authenticate(authenticate);
        } catch (Exception e) {
            throw new CustomException(
                    "이메일 또는 비밀번호가 올바르지 않습니다.",
                    ErrorCode.UNAUTHORIZED
            );
        }

        CustomUserDetails userDetails =
                (CustomUserDetails) authentication.getPrincipal();

        Long userId = userDetails.getUserId();

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new CustomException("해당 유저가 존재하지 않습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        //인증받은 Authentication을 통해 token을 발급 받음
        String accessToken = jwtTokenProvider.createAccessToken(authentication);
        String refreshToken = jwtTokenProvider.createRefreshToken(userId);

        refreshTokenRedisService.save(
                userId,
                refreshToken,
                Duration.ofMillis(jwtTokenProvider.getRefreshTokenValidTime())
        );

        return new LoginTokenResult(accessToken, refreshToken, user);
    }

    @Transactional(readOnly = true)
    public UserResponseDto getUserProfile(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new CustomException("유저 정보를 찾을 수 없습니다", ErrorCode.RESOURCE_NOT_FOUND));

        return UserResponseDto.from(user);
    }

    public UserResponseDto updateProfile(Long userId, UpdateUserProfileRequestDto updateUserProfileRequestDto) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new CustomException("해당 유저가 존재하지 않습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        if (updateUserProfileRequestDto.getNickname() != null) {
            if (userRepository.existsByNickname(updateUserProfileRequestDto.getNickname())
                    && !user.getNickname().equals(updateUserProfileRequestDto.getNickname())) {
                throw new CustomException("이미 존재하는 닉네임입니다.", ErrorCode.DUPLICATE_RESOURCE);
            }
        }

        user.updateProfile(
                updateUserProfileRequestDto.getName(),
                updateUserProfileRequestDto.getNickname(),
                updateUserProfileRequestDto.getAge(),
                updateUserProfileRequestDto.getCodingLevel()
        );

        return getUserProfile(userId);
    }

    public LoginTokenResult reissueToken(String refreshToken) {

        if (refreshToken == null || refreshToken.isBlank()) {
            throw new CustomException(
                    "Refresh Token이 존재하지 않습니다.",
                    ErrorCode.UNAUTHORIZED
            );
        }

        // Refresh Token 유효성 검증 (JWT 서명, 만료 여부)
        jwtTokenProvider.isValidateToken(refreshToken);

        // Refresh Token에서 userId 추출
        Long userId = jwtTokenProvider.getUserIdFromToken(refreshToken);

        // Redis에 저장된 토큰과 일치 여부 확인
        refreshTokenRedisService.validate(userId, refreshToken);

        // User 조회 (인증 객체 생성을 위해)
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new CustomException("해당 유저가 존재하지 않습니다.", ErrorCode.RESOURCE_NOT_FOUND));

        // 인증 객체 생성
        CustomUserDetails userDetails = new CustomUserDetails(
                userId,
                user.getEmail(),
                null,
                java.util.Collections.emptyList()
        );

        Authentication authentication = new UsernamePasswordAuthenticationToken(
                userDetails,
                "",
                java.util.Collections.emptyList()
        );

        // 새로운 Access Token 생성
        String newAccessToken = jwtTokenProvider.createAccessToken(authentication);

        // 새로운 Refresh Token 생성
        String newRefreshToken = jwtTokenProvider.createRefreshToken(userId);

        // Redis에 새로운 Refresh Token 저장 (기존 토큰 교체)
        refreshTokenRedisService.save(
                userId,
                newRefreshToken,
                Duration.ofMillis(jwtTokenProvider.getRefreshTokenValidTime())
        );

        return new LoginTokenResult(newAccessToken, newRefreshToken, user);
    }
}
