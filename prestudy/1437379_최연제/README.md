작성일: 2026-01-16  
작성자: 최연제  
학번: 1437379  

# Spring Boot REST API 정리

## REST API란?

REST(Representational State Transfer)는 HTTP 프로토콜을 기반으로 자원(Resource)을 정의하고 상태를 주고받는 아키텍처 스타일입니다.

## REST의 핵심 원칙

### 1. 자원(Resource) - URI로 표현

모든 자원은 고유한 URI를 가지며, 명사형으로 표현합니다.

```
✅ Good: /api/users, /api/products
❌ Bad: /api/getUsers, /api/createProduct
```

### 2. 행위(Verb) - HTTP 메서드로 표현

- GET: 조회
- POST: 생성
- PUT: 전체 수정
- PATCH: 부분 수정
- DELETE: 삭제

### 3. 표현(Representation)

주로 JSON 형식으로 데이터를 주고받습니다. XML, Plain Text 등도 가능합니다.

## Spring Boot에서 REST API 구현

### @RestController

REST API를 제공하는 컨트롤러임을 명시합니다.

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    // REST API 메서드들
}
```

### 주요 어노테이션

#### HTTP 메서드 매핑

```java
@GetMapping        // 조회
@PostMapping       // 생성
@PutMapping        // 전체 수정
@PatchMapping      // 부분 수정
@DeleteMapping     // 삭제
```

#### 파라미터 바인딩

```java
@PathVariable      // URI 경로에서 값 추출
@RequestParam      // 쿼리 파라미터에서 값 추출
@RequestBody       // HTTP Body에서 JSON 데이터 추출
```

## 실제 구현 예제

### 기본 CRUD 구현

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    // 전체 조회
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.findAll();
        return ResponseEntity.ok(users);
    }
    
    // 단건 조회
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        User user = userService.findById(id);
        return ResponseEntity.ok(user);
    }
    
    // 생성
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        User savedUser = userService.save(user);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedUser);
    }
    
    // 전체 수정
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody User user) {
        User updatedUser = userService.update(id, user);
        return ResponseEntity.ok(updatedUser);
    }
    
    // 부분 수정
    @PatchMapping("/{id}")
    public ResponseEntity<User> patchUser(@PathVariable Long id, @RequestBody Map<String, Object> updates) {
        User patchedUser = userService.patch(id, updates);
        return ResponseEntity.ok(patchedUser);
    }
    
    // 삭제
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

### 쿼리 파라미터 사용

```java
// GET /api/users/search?name=김철수&age=25
@GetMapping("/search")
public ResponseEntity<List<User>> searchUsers(@RequestParam String name, @RequestParam(required = false) Integer age) {
    List<User> users = userService.search(name, age);
    return ResponseEntity.ok(users);
}
```

## HTTP 상태 코드

### 성공 응답 (2xx)

- `200 OK`: 요청 성공
- `201 Created`: 리소스 생성 성공
- `204 No Content`: 성공했지만 응답 본문 없음 (주로 DELETE)

### 클라이언트 에러 (4xx)

- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 필요
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음

### 서버 에러 (5xx)

- `500 Internal Server Error`: 서버 내부 오류
- `503 Service Unavailable`: 서비스 이용 불가

## ResponseEntity 활용

```java
// 성공 응답
return ResponseEntity.ok(data);
return ResponseEntity.status(HttpStatus.CREATED).body(data);

// 에러 응답
return ResponseEntity.notFound().build();
return ResponseEntity.badRequest().body(errorMessage);

// 커스텀 헤더 추가
return ResponseEntity.ok().header("Custom-Header", "value").body(data);
```

## DTO (Data Transfer Object) 패턴

### 요청/응답 DTO 분리

```java
// 요청 DTO
@Getter
@Setter
public class UserCreateRequest {
    private String username;
    private String email;
    private String password;
}

// 응답 DTO
@Getter
@Setter
public class UserResponse {
    private Long id;
    private String username;
    private String email;
    private LocalDateTime createdAt;
}

// Controller
@PostMapping
public ResponseEntity<UserResponse> createUser(@RequestBody UserCreateRequest request) {
    UserResponse response = userService.createUser(request);
    return ResponseEntity.status(HttpStatus.CREATED).body(response);
}
```

## 예외 처리

### @ControllerAdvice를 활용한 전역 예외 처리

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        ErrorResponse error = new ErrorResponse(404, e.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception e) {
        ErrorResponse error = new ErrorResponse(500, "Internal Server Error");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
```

## Validation (유효성 검증)

### Bean Validation 사용

```java
// DTO
@Getter
@Setter
public class UserCreateRequest {
    
    @NotBlank(message = "사용자명은 필수입니다")
    @Size(min = 3, max = 20, message = "사용자명은 3-20자여야 합니다")
    private String username;
    
    @NotBlank(message = "이메일은 필수입니다")
    @Email(message = "올바른 이메일 형식이 아닙니다")
    private String email;
    
    @NotBlank(message = "비밀번호는 필수입니다")
    @Size(min = 8, message = "비밀번호는 최소 8자 이상이어야 합니다")
    private String password;
}

// Controller
@PostMapping
public ResponseEntity<UserResponse> createUser(@Valid @RequestBody UserCreateRequest request) {
    // @Valid 어노테이션으로 자동 검증
    UserResponse response = userService.createUser(request);
    return ResponseEntity.status(HttpStatus.CREATED).body(response);
}
```

## REST API 설계 Best Practices

1. 명사형 URI 사용: `/users`, `/products`
2. 계층 구조 표현: `/users/{userId}/orders/{orderId}`
3. 복수형 사용: `/users` (not `/user`)
4. 소문자 사용: `/api/users` (not `/API/Users`)
5. 하이픈 사용: `/order-items` (not `/order_items`)
6. 버전 관리: `/api/v1/users`
7. 적절한 HTTP 메서드 사용
8. 적절한 상태 코드 반환

## 참고 사항

- `@RestController` = `@Controller` + `@ResponseBody`
- Jackson 라이브러리가 자동으로 객체를 JSON으로 변환
- Spring Boot는 기본적으로 JSON 변환을 지원
- Content-Type: application/json 자동 설정

## 추가 학습 자료

- Spring Boot 공식 문서: https://spring.io/projects/spring-boot
- REST API 설계 가이드
- HTTP 프로토콜 심화 학습
- Spring Security를 통한 API 인증/인가