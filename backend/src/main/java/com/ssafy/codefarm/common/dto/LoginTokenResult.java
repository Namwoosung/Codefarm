package com.ssafy.codefarm.common.dto;

import com.ssafy.codefarm.user.entity.User;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class LoginTokenResult {

    private final String accessToken;
    private final String refreshToken;
    private final User user;
}
