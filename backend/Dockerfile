# syntax=docker/dockerfile:1

########################
# 1) Build stage
########################
FROM gradle:9.2.1-jdk17-alpine AS builder
WORKDIR /app

# (선택) 빌드 속도/재현성을 위해 Gradle 사용자 홈을 고정
ENV GRADLE_USER_HOME=/home/gradle/.gradle

# 1) 의존성 캐시를 최대한 살리기 위해 "먼저" 빌드 스크립트만 복사
# - 프로젝트 구조에 맞게 파일명이 다르면 수정하세요.
COPY build.gradle settings.gradle ./
COPY gradle ./gradle
COPY gradlew ./
RUN chmod +x gradlew

# 2) 의존성만 미리 받아 캐시 (소스 없이 실행)
# - 테스트는 CI에서 분리하고 싶으면 -x test 유지
RUN ./gradlew --no-daemon dependencies -x test || true

# 3) 이제 소스 복사
COPY src ./src

# 4) 실제 산출물(JAR) 만들기
RUN ./gradlew --no-daemon clean bootJar -x test


########################
# 2) Runtime stage
########################
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# (선택) 보안: non-root 유저로 실행
RUN addgroup -S spring && adduser -S spring -G spring
USER spring

# bootJar 결과 복사 (파일명은 프로젝트에 따라 다름)
COPY --from=builder /app/build/libs/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
