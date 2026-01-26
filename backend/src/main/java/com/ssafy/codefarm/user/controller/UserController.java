package com.ssafy.codefarm.user.controller;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.user.dto.request.*;
import com.ssafy.codefarm.user.dto.response.*;
import com.ssafy.codefarm.user.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/users")
public class UserController {

    private final UserService userService;

    @PostMapping("/signup")
    @ResponseStatus(HttpStatus.CREATED)
    public SuccessResponse signup(@RequestBody @Valid UserSignupRequestDto userSignupRequestDto) {
        UserResponseDto userResponseDto = userService.signup(userSignupRequestDto);
        return SuccessResponse.success("회원가입에 성공했습니다.", userResponseDto);
    }

    @PostMapping("/check/emails")
    @ResponseStatus(HttpStatus.OK)
    public SuccessResponse checkEmailDuplicate(
            @RequestBody @Valid CheckEmailRequestDto checkEmailRequestDto
    ) {

        CheckEmailResponseDto checkEmailResponseDto =
                userService.checkEmailDuplicate(checkEmailRequestDto);

        String message = checkEmailResponseDto.isAvailable()
                ? "사용 가능한 이메일입니다."
                : "이미 존재하는 이메일입니다.";

        return SuccessResponse.success(message, checkEmailResponseDto);
    }

    @PostMapping("/check/nicknames")
    @ResponseStatus(HttpStatus.OK)
    public SuccessResponse checkNicknameDuplicate(
            @RequestBody @Valid CheckNicknameRequestDto checkNicknameRequestDto
    ) {

        CheckNicknameResponseDto checkNicknameResponseDto =
                userService.checkNicknameDuplicate(checkNicknameRequestDto);

        String message = checkNicknameResponseDto.isAvailable()
                ? "사용 가능한 닉네임입니다."
                : "이미 존재하는 닉네임입니다.";

        return SuccessResponse.success(message, checkNicknameResponseDto);
    }

    @PostMapping("/login")
    @ResponseStatus(HttpStatus.OK)
    public SuccessResponse login(
            @RequestBody @Valid LoginRequestDto loginRequestDto
    ) {

        LoginResponseDto loginResponseDto =
                userService.login(loginRequestDto);

        return SuccessResponse.success(
                "로그인에 성공했습니다.",
                loginResponseDto
        );
    }

    @PostMapping("/logout")
    @ResponseStatus(HttpStatus.OK)
    public SuccessResponse logout() {

        // Stateless이므로 서버에서 할 작업 없음
        // 클라이언트가 accessToken 삭제하면 끝
        // 추후 refresh token 도입 후 추가 작업 진행

        return SuccessResponse.success("로그아웃 성공", null);
    }

    @GetMapping("/profiles")
    public SuccessResponse getMyProfile(
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {

        UserResponseDto userResponseDto = userService.getUserProfile(userDetails.getUserId());

        return SuccessResponse.success("유저 정보 조회 성공", userResponseDto);
    }

    @PatchMapping("/profiles")
    public SuccessResponse updateProfile(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            @RequestBody @Valid UpdateUserProfileRequestDto updateUserProfileRequestDto
    ) {
        UserResponseDto userResponseDto = userService.updateProfile(userDetails.getUserId(), updateUserProfileRequestDto);

        return SuccessResponse.success("유저 정보 수정 성공", userResponseDto);
    }

}
