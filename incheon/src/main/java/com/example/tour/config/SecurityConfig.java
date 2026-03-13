package com.example.tour.config;

import com.example.tour.service.MemberService;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@RequiredArgsConstructor
public class SecurityConfig {

    private final MemberService memberService;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(
                                "/", "/error",
                                "/member/login", "/member/terms", "/member/join", "/member/check-id",
                                "/policy/**", "/spot/**",
                                "/notice/list", "/notice/detail/**",
                                "/css/**", "/js/**", "/images/**", "/fonts/**"
                        ).permitAll()
                        .requestMatchers(
                                "/notice/write", "/notice/edit/**", "/notice/delete/**"
                        ).hasRole("ADMIN")
                        .requestMatchers(
                                "/review/list", "/review/detail/**",
                                "/review/write", "/review/edit/**", "/review/delete/**",
                                "/member/mypage", "/uploads/**"
                        ).authenticated()
                        .requestMatchers("/member/manage").hasRole("ADMIN")
                        .anyRequest().authenticated()
                )
                .formLogin(form -> form
                        .loginPage("/member/login")
                        .loginProcessingUrl("/login")
                        .usernameParameter("id")
                        .passwordParameter("pw")
                        .defaultSuccessUrl("/", true)
                        .permitAll()
                )
                .logout(logout -> logout
                        .logoutUrl("/logout")
                        .logoutSuccessUrl("/member/login")
                );

        return http.build();
    }

    @Bean
    public UserDetailsService userDetailsService() {
        return loginId -> {
            var member = memberService.findByLoginId(loginId);
            return User.builder()
                    .username(member.getLoginId())
                    .password(member.getPasswordHash())
                    .roles(member.getRole().name())
                    .build();
        };
    }
}
