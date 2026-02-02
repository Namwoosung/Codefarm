package com.ssafy.codefarm.common.authority;

import com.ssafy.codefarm.common.dto.CustomUserDetails;
import com.ssafy.codefarm.common.exception.CustomException;
import com.ssafy.codefarm.common.exception.ErrorCode;
import io.jsonwebtoken.*;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import java.security.Key;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

@Component
@Slf4j
public class JwtTokenProvider {

    private final Key key;
    private final long accessTokenValidTime;
    private final long refreshTokenValidTime;

    private static final String CLAIM_AUTH = "auth";
    private static final String CLAIM_TYPE = "type";
    private static final String TOKEN_TYPE_ACCESS = "access";
    private static final String TOKEN_TYPE_REFRESH = "refresh";

    public JwtTokenProvider(
            @Value("${jwt.secret-key}") String secretKey,
            @Value("${jwt.access-expiration}") long accessTokenValidTime,
            @Value("${jwt.refresh-expiration}") long refreshTokenValidTime
    ) {
        this.key = Keys.hmacShaKeyFor(Decoders.BASE64.decode(secretKey));
        this.accessTokenValidTime = accessTokenValidTime;
        this.refreshTokenValidTime = refreshTokenValidTime;
    }

    public String createAccessToken(Authentication authentication) {

        if (!(authentication.getPrincipal() instanceof CustomUserDetails userDetails)) {
            throw new CustomException(
                    "Invalid authentication principal",
                    ErrorCode.FORBIDDEN
            );
        }

        Long userId = userDetails.getUserId();

        String authorities = authentication.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.joining(","));

        Date now = new Date();
        Date expiry = new Date(now.getTime() + accessTokenValidTime);

        return Jwts.builder()
                .setSubject(String.valueOf(userId))
                .claim(CLAIM_AUTH, authorities)
                .claim(CLAIM_TYPE, TOKEN_TYPE_ACCESS)
                .setIssuedAt(now)
                .setExpiration(expiry)
                .signWith(key, SignatureAlgorithm.HS256)
                .compact();
    }

    public String createRefreshToken(Long userId) {

        Date now = new Date();
        Date expiry = new Date(now.getTime() + refreshTokenValidTime);

        return Jwts.builder()
                .setSubject(String.valueOf(userId))
                .claim(CLAIM_TYPE, TOKEN_TYPE_REFRESH)
                .setIssuedAt(now)
                .setExpiration(expiry)
                .signWith(key, SignatureAlgorithm.HS256)
                .compact();
    }

    public void isValidateToken(String token) {
        try {
            Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(token);
        } catch (MalformedJwtException e) {
            log.warn("INVALID JWT TOKEN : {}", e.getMessage());
            throw new CustomException("잘못된 JWT 서명입니다.", ErrorCode.INVALID_TOKEN);
        } catch (ExpiredJwtException e) {
            log.warn("EXPIRED JWT TOKEN : {}", e.getMessage());
            throw new CustomException("토큰이 만료되었습니다.", ErrorCode.EXPIRED_TOKEN);
        } catch (UnsupportedJwtException e) {
            log.warn("UNSUPPORTED JWT TOKEN : {}", e.getMessage());
            throw new CustomException("지원하지 않는 JWT 토큰입니다.", ErrorCode.INVALID_TOKEN);
        } catch (IllegalArgumentException e) {
            log.warn("JWT CLAIM IS EMPTY : {}", e.getMessage());
            throw new CustomException("JWT 토큰이 비어있습니다.", ErrorCode.INVALID_TOKEN);
        }
    }


    public Authentication getAuthentication(String token) {

        Claims claims = getClaims(token);

        String type = claims.get(CLAIM_TYPE, String.class);

        if (TOKEN_TYPE_REFRESH.equals(type)) {
            throw new CustomException("Refresh Token으로 인증할 수 없습니다.", ErrorCode.INVALID_TOKEN);
        }

        Long userId = Long.parseLong(claims.getSubject());

        String auth = claims.get("auth", String.class);

        List<GrantedAuthority> authorities =
                (auth == null || auth.isBlank())
                        ? Collections.emptyList()
                        : Arrays.stream(auth.split(","))
                        .map(SimpleGrantedAuthority::new)
                        .collect(Collectors.toList());

        UserDetails principal =
                new CustomUserDetails(userId, "", "", authorities);

        return new UsernamePasswordAuthenticationToken(
                principal,
                "",
                authorities
        );
    }

    public Long getUserIdFromToken(String token) {

        Claims claims = getClaims(token);

        String type = claims.get(CLAIM_TYPE, String.class);

        if (!TOKEN_TYPE_REFRESH.equals(type)) {
            throw new CustomException("Refresh Token이 아닙니다.", ErrorCode.INVALID_TOKEN);
        }

        return Long.parseLong(claims.getSubject());
    }


    private Claims getClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }
}
