package com.example.tour.dto;

import com.example.tour.domain.Member;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class MemberMyPageDto {

    private Long id;
    private String loginId;
    private String email;
    private String phone;
    private String role;
    private LocalDateTime createdAt;

    public MemberMyPageDto(Member member) {
        this.id = member.getId();
        this.loginId = member.getLoginId();
        this.email = member.getEmail();
        this.phone = member.getPhone();
        this.role = member.getRole().name();
        this.createdAt = member.getCreatedAt();
    }
}