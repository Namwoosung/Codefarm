package com.ssafy.codefarm.common.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.ClientHttpRequestFactory;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

import java.net.http.HttpClient;
import java.time.Duration;

@Slf4j
@Configuration
public class HttpClientConfig {

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

    @Value("${ai-hint.server.base-url}")
    private String aiHintBaseUrl;

    @Value("${ai-hint.server.connect-timeout-ms}")
    private int aiHintConnectTimeoutMs;

    @Value("${ai-hint.server.read-timeout-ms}")
    private int aiHintReadTimeoutMs;

    private ClientHttpRequestFactory createRequestFactory(int connectTimeout, int readTimeout) {
        JdkClientHttpRequestFactory factory =
                new JdkClientHttpRequestFactory(
                        HttpClient.newBuilder()
                                .connectTimeout(Duration.ofMillis(connectTimeout))
                                .build()
                );

        factory.setReadTimeout(readTimeout);
        return factory;
    }

    @Bean
    public RestClient executionRestClient() {
        return RestClient.builder()
                .baseUrl(executionBaseUrl)
                .requestFactory(createRequestFactory(
                        executionConnectTimeoutMs,
                        executionReadTimeoutMs
                ))
                .build();
    }

    @Bean
    public RestClient feedbackRestClient() {
        return RestClient.builder()
                .baseUrl(feedbackBaseUrl)
                .requestFactory(createRequestFactory(
                        feedbackConnectTimeoutMs,
                        feedbackReadTimeoutMs
                ))
                .build();
    }

    @Bean
    public RestClient aiHintRestClient() {
        return RestClient.builder()
                .baseUrl(aiHintBaseUrl)
                .requestFactory(createRequestFactory(
                        aiHintConnectTimeoutMs,
                        aiHintReadTimeoutMs
                ))
                .build();
    }
}
