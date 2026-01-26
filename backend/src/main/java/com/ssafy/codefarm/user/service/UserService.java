package com.ssafy.codefarm.user.service;

import com.ssafy.codefarm.common.authority.JwtTokenProvider;
import com.ssafy.codefarm.common.dto.CustomUserDetails;
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

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;

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
    public LoginResponseDto login(LoginRequestDto loginRequestDto) {
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

        //인증받은 Authentication을 통해 token을 발급 받음
        String accessToken = jwtTokenProvider.createAccessToken(authentication);

        CustomUserDetails userDetails =
                (CustomUserDetails) authentication.getPrincipal();

        User user = userRepository.findById(userDetails.getUserId())
                        .orElseThrow(() -> new CustomException(
                                        "해당 유저가 존재하지 않습니다.",
                                        ErrorCode.RESOURCE_NOT_FOUND
                                ));

        return LoginResponseDto.from(
                UserResponseDto.from(user),
                TokenResponseDto.from(accessToken)
        );



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
}
