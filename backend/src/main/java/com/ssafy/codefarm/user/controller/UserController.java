package com.ssafy.codefarm.user.controller;

import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.user.dto.request.CheckEmailRequestDto;
import com.ssafy.codefarm.user.dto.request.CheckNicknameRequestDto;
import com.ssafy.codefarm.user.dto.request.UserSignupRequestDto;
import com.ssafy.codefarm.user.dto.response.CheckEmailResponseDto;
import com.ssafy.codefarm.user.dto.response.CheckNicknameResponseDto;
import com.ssafy.codefarm.user.dto.response.UserSignupResponseDto;
import com.ssafy.codefarm.user.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
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
        UserSignupResponseDto userSignupResponseDto = userService.signup(userSignupRequestDto);
        return SuccessResponse.success("회원가입에 성공했습니다.", userSignupResponseDto);
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

}
