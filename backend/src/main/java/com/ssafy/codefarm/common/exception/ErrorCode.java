package com.ssafy.codefarm.common.exception;

import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum ErrorCode {

    /* =========================
     * 400 - BAD REQUEST
     * ========================= */

    BAD_REQUEST(HttpStatus.BAD_REQUEST, "BAD_REQUEST"),
    INVALID_PARAMETER(HttpStatus.BAD_REQUEST, "INVALID_PARAMETER"),
    MISSING_PARAMETER(HttpStatus.BAD_REQUEST, "MISSING_PARAMETER"),
    TYPE_MISMATCH(HttpStatus.BAD_REQUEST, "TYPE_MISMATCH"),

    /* =========================
     * 401 - UNAUTHORIZED
     * ========================= */

    UNAUTHORIZED(HttpStatus.UNAUTHORIZED, "UNAUTHORIZED"),
    INVALID_TOKEN(HttpStatus.UNAUTHORIZED, "INVALID_TOKEN"),
    EXPIRED_TOKEN(HttpStatus.UNAUTHORIZED, "EXPIRED_TOKEN"),

    /* =========================
     * 403 - FORBIDDEN
     * ========================= */

    FORBIDDEN(HttpStatus.FORBIDDEN, "FORBIDDEN"),

    /* =========================
     * 404 - NOT FOUND
     * ========================= */

    RESOURCE_NOT_FOUND(HttpStatus.NOT_FOUND, "RESOURCE_NOT_FOUND"),

    /* =========================
     * 409 - CONFLICT
     * ========================= */

    DUPLICATE_RESOURCE(HttpStatus.CONFLICT, "DUPLICATE_RESOURCE"),

    /* =========================
     * 413 - PAYLOAD TOO LARGE
     * ========================= */

    FILE_TOO_LARGE(HttpStatus.PAYLOAD_TOO_LARGE, "FILE_TOO_LARGE"),

    /* =========================
     * 500 - SERVER ERROR
     * ========================= */

    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_SERVER_ERROR"),
    DATABASE_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "DATABASE_ERROR"),

    /* =========================
     * 502 / 504 - EXTERNAL
     * ========================= */

    EXTERNAL_API_ERROR(HttpStatus.BAD_GATEWAY, "EXTERNAL_API_ERROR"),
    TIMEOUT_ERROR(HttpStatus.GATEWAY_TIMEOUT, "TIMEOUT_ERROR");

    private final HttpStatus httpStatusCode;
    private final String errorCode;
}
