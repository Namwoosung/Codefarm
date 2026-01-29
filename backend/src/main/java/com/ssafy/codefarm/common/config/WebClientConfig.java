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

    // execution
    @Value("${execution.server.base-url}")
    private String executionBaseUrl;

    @Value("${execution.server.connect-timeout-ms}")
    private int executionConnectTimeoutMs;

    @Value("${execution.server.read-timeout-ms}")
    private int executionReadTimeoutMs;

    // feedback
    @Value("${feedback.server.base-url}")
    private String feedbackBaseUrl;

    @Value("${feedback.server.connect-timeout-ms}")
    private int feedbackConnectTimeoutMs;

    @Value("${feedback.server.read-timeout-ms}")
    private int feedbackReadTimeoutMs;


    private HttpClient createHttpClient(int connectTimeout, int readTimeout) {
        return HttpClient.create()
            .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, connectTimeout)
            .responseTimeout(Duration.ofMillis(readTimeout))
            .doOnConnected(conn ->
                conn.addHandlerLast(
                    new ReadTimeoutHandler(readTimeout, TimeUnit.MILLISECONDS)
                )
            );
    }

    @Bean
    public WebClient executionWebClient() {
        return WebClient.builder()
            .baseUrl(executionBaseUrl)
            .clientConnector(
                new ReactorClientHttpConnector(
                    createHttpClient(
                        executionConnectTimeoutMs,
                        executionReadTimeoutMs
                    )
                )
            )
            .build();
    }

    @Bean
    public WebClient feedbackWebClient() {
        return WebClient.builder()
            .baseUrl(feedbackBaseUrl)
            .clientConnector(
                new ReactorClientHttpConnector(
                    createHttpClient(
                        feedbackConnectTimeoutMs,
                        feedbackReadTimeoutMs
                    )
                )
            )
            .build();
    }
}