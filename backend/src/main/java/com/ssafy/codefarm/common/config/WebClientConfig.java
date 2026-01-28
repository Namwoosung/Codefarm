package com.ssafy.codefarm.common.config;

import io.netty.channel.ChannelOption;
import io.netty.handler.timeout.ReadTimeoutHandler;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;

import java.time.Duration;
import java.util.concurrent.TimeUnit;

@Slf4j
@Configuration
public class WebClientConfig {
    @Value("${execution.server.base-url}")
    private String baseUrl;

    @Value("${execution.server.connect-timeout-ms}")
    private int connectTimeoutMs;

    @Value("${execution.server.read-timeout-ms}")
    private int readTimeoutMs;

    @Bean
    public WebClient executionWebClient() {

        HttpClient httpClient = HttpClient.create()
                // TCP 연결 제한 시간
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, connectTimeoutMs)
                // 응답 전체 타임아웃
                .responseTimeout(Duration.ofMillis(readTimeoutMs))
                // 실제 읽기 타임아웃 (소켓 레벨)
                .doOnConnected(conn ->
                        conn.addHandlerLast(
                                new ReadTimeoutHandler(readTimeoutMs, TimeUnit.MILLISECONDS)
                        )
                );

        return WebClient.builder()
                .baseUrl(baseUrl)
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .build();
    }

}
