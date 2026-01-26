package com.ssafy.codefarm.user.controller;

import com.ssafy.codefarm.common.dto.SuccessResponse;
import com.ssafy.codefarm.user.dto.request.UserSignupRequestDto;
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

}
