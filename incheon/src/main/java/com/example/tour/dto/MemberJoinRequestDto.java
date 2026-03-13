package com.example.tour.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class MemberJoinRequestDto {
    private String id;
    private String pw;
    private String pw2;
    private String email;
    private String tel;
}