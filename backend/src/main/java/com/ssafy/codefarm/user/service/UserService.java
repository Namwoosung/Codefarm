package com.ssafy.codefarm.user.service;

import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import com.ssafy.codefarm.user.dto.request.CheckEmailRequestDto;
import com.ssafy.codefarm.user.dto.request.CheckNicknameRequestDto;
import com.ssafy.codefarm.user.dto.request.UserSignupRequestDto;
import com.ssafy.codefarm.user.dto.response.CheckEmailResponseDto;
import com.ssafy.codefarm.user.dto.response.CheckNicknameResponseDto;
import com.ssafy.codefarm.user.dto.response.UserSignupResponseDto;
import com.ssafy.codefarm.user.entity.User;
import com.ssafy.codefarm.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
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

    public UserSignupResponseDto signup(UserSignupRequestDto userSignupRequestDto) {
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

        return UserSignupResponseDto.from(user);
    }

    @Transactional(readOnly = true)
    public CheckEmailResponseDto checkEmailDuplicate(CheckEmailRequestDto checkEmailRequestDto) {
        return new CheckEmailResponseDto(!userRepository.existsByEmail(checkEmailRequestDto.getEmail()));
    }

    @Transactional(readOnly = true)
    public CheckNicknameResponseDto checkNicknameDuplicate(CheckNicknameRequestDto checkNicknameRequestDto) {
        return new CheckNicknameResponseDto(!userRepository.existsByNickname(checkNicknameRequestDto.getNickname()));
    }
}
