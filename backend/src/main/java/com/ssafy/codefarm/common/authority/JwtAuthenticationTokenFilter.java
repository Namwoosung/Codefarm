package com.ssafy.codefarm.common.authority;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.dto.ErrorResponse;
import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.InsufficientAuthenticationException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Slf4j
@RequiredArgsConstructor
public class JwtAuthenticationTokenFilter extends OncePerRequestFilter {

    private static final String BEARER_PREFIX = "Bearer ";
    private static final int BEARER_PREFIX_LENGTH = 7;

    private final JwtTokenProvider jwtTokenProvider;

    private final AuthenticationEntryPoint authenticationEntryPoint;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        // OPTIONS 요청은 통과 (CORS preflight)
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            filterChain.doFilter(request, response);
            return;
        }

        try {
            String token = resolveToken(request);

            // 토큰 존재 & 아직 인증 안 된 경우
            if (StringUtils.hasText(token)
                    && SecurityContextHolder.getContext().getAuthentication() == null) {

                // 토큰 검증
                jwtTokenProvider.isValidateToken(token);

                // Authentication 생성
                Authentication authentication = jwtTokenProvider.getAuthentication(token);

                // SecurityContext에 저장
                SecurityContextHolder.getContext().setAuthentication(authentication);

                log.debug("JWT authentication success. userId={}",
                        ((CustomUserDetails)authentication.getPrincipal()).getUserId());
            }

        } catch (CustomException e) {
            // JWT 검증 실패 → 인증 정보 제거
            SecurityContextHolder.clearContext();
            log.warn("JWT authentication failed: {}", e.getMessage());


            // 만룍 토큰은 만료로 response
            if (e.getErrorCode() == ErrorCode.EXPIRED_TOKEN) {

                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.setContentType("application/json");
                response.setCharacterEncoding("UTF-8");

                ErrorResponse errorResponse =
                        new ErrorResponse("ACCESS_TOKEN_EXPIRED", "Access Token이 만료되었습니다.");

                response.getWriter()
                        .write(new ObjectMapper().writeValueAsString(errorResponse));

                return;

            }

            // 나머지는 그냥 인증 실패 처리
            authenticationEntryPoint.commence(
                    request,
                    response,
                    new InsufficientAuthenticationException("Invalid Token")
            );
            return;
        }

        filterChain.doFilter(request, response);
    }

    /**
     * Authorization 헤더에서 Bearer 토큰 추출
     */
    private String resolveToken(HttpServletRequest request) {

        String bearerToken = request.getHeader("Authorization");

        if (StringUtils.hasText(bearerToken)
                && bearerToken.startsWith(BEARER_PREFIX)) {

            return bearerToken.substring(BEARER_PREFIX_LENGTH);
        }

        return null;
    }

    @Override
    protected boolean shouldNotFilterAsyncDispatch() {
        return false; // ASYNC dispatch에서도 필터 실행
    }

    @Override
    protected boolean shouldNotFilterErrorDispatch() {
        return false; // ERROR dispatch에서도 필터 실행
    }
}
